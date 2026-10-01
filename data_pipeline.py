from __future__ import annotations
import io
import re
import zipfile
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

GPPS_URL = "https://www.gp-patient.co.uk/FileDownload/Download?fileRedirect=2026%2Fsurvey-results%2Fpractice-results%2Fpractice-data-csv%2FGPPS_2026_Practice_data_%28weighted%29_%28csv%29_PUBLIC.csv"
REGISTRATION_PAGE = "https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice/september-2026"
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/154 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}


def _get(url: str, timeout: int = 30) -> requests.Response:
    response = requests.get(url, timeout=timeout, headers=HTTP_HEADERS)
    response.raise_for_status()
    return response


def _normalise_percent(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().empty:
        return s
    if s.dropna().quantile(0.9) <= 1.01:
        s = s * 100
    return s.where((s >= 0) & (s <= 100))


def _pick(columns, patterns):
    lower = {str(c).lower(): c for c in columns}
    for p in patterns:
        if p.lower() in lower:
            return lower[p.lower()]
    for c in columns:
        lc = str(c).lower()
        if any(re.search(p, lc) for p in patterns if p.startswith("^")):
            return c
    return None


def _easy_summary(df: pd.DataFrame, stem: str, legacy_patterns: list[str]) -> pd.Series:
    combined = _pick(df.columns, legacy_patterns)
    if combined is not None:
        return _normalise_percent(df[combined])

    very_easy = _pick(df.columns, [f"{stem}_2.pct"])
    fairly_easy = _pick(df.columns, [f"{stem}_3.pct"])
    if very_easy is None or fairly_easy is None:
        return pd.Series(pd.NA, index=df.index, dtype="Float64")

    first = _normalise_percent(df[very_easy])
    second = _normalise_percent(df[fairly_easy])
    return (first + second).clip(lower=0, upper=100)


def parse_gpps(df: pd.DataFrame) -> pd.DataFrame:
    code = _pick(df.columns, ["ad_practicecode", "practice_code", "prac_code"])
    name = _pick(df.columns, ["ad_practicename", "practice_name", "prac_name"])
    ics = _pick(df.columns, ["ad_icsname", "ics_name", "icb_name"])

    phone_easy = _easy_summary(df, "localgpservicesphone", ["q1_12pct", "q1_1_2pct", r"^q1.*12pct$"])
    website_easy = _easy_summary(df, "localgpserviceswebsite", ["q2_12pct", "q2_1_2pct", r"^q2.*12pct$"])
    app_easy = _easy_summary(df, "localgpservicesapp", ["q3_12pct", "q3_1_2pct", r"^q3.*12pct$"])

    missing = [
        label
        for label, value in {
            "practice code": code,
            "practice name": name,
            "phone ease": phone_easy.notna().any(),
        }.items()
        if value is None or value is False
    ]
    if missing:
        raise ValueError("GPPS columns not recognised: " + ", ".join(missing))

    out = pd.DataFrame(
        {
            "practice_code": df[code].astype(str).str.strip(),
            "practice_name": df[name].astype(str).str.strip(),
            "ics_name": df[ics].astype(str).str.strip() if ics else "",
            "phone_easy_pct": phone_easy,
            "website_easy_pct": website_easy,
            "app_easy_pct": app_easy,
        }
    )
    out = out[out["practice_code"].ne("") & out["practice_code"].ne("nan")]
    return out.drop_duplicates("practice_code")


def fetch_gpps(timeout=30) -> pd.DataFrame:
    r = _get(GPPS_URL, timeout=timeout)
    return parse_gpps(pd.read_csv(io.BytesIO(r.content), low_memory=False))


def _find_download_link(page_url: str, text_fragment: str, timeout=30) -> str:
    r = _get(page_url, timeout=timeout)
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        text = " ".join(a.stripped_strings)
        if text_fragment.lower() in text.lower():
            return urljoin(page_url, a["href"])
    raise ValueError(f"Could not find download link containing: {text_fragment}")


def parse_registered_patients(df: pd.DataFrame) -> pd.DataFrame:
    code = _pick(df.columns, ["code", "practice_code", "prac_code", r"^.*practice.*code.*$"])
    n = _pick(df.columns, ["number_of_patients", "number of patients", "patients", r"^.*number.*patients.*$"])
    if code is None or n is None:
        raise ValueError("Registered-patient columns not recognised")
    out = pd.DataFrame(
        {
            "practice_code": df[code].astype(str).str.strip(),
            "list_size": pd.to_numeric(df[n], errors="coerce"),
        }
    )
    return out.dropna(subset=["list_size"]).drop_duplicates("practice_code")


def fetch_registered_patients(timeout=30) -> pd.DataFrame:
    url = _find_download_link(REGISTRATION_PAGE, "Totals (GP practice-all persons)", timeout=timeout)
    r = _get(url, timeout=timeout)
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        csvs = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csvs:
            raise ValueError("Patient registration ZIP contained no CSV")
        with zf.open(csvs[0]) as f:
            return parse_registered_patients(pd.read_csv(f, low_memory=False))


def load_public_context() -> pd.DataFrame:
    gpps = fetch_gpps()
    try:
        registered = fetch_registered_patients()
        merged = gpps.merge(registered, on="practice_code", how="left")
    except Exception:
        merged = gpps.copy()
        merged["list_size"] = pd.NA
    return merged
