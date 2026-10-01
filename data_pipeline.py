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


def _normalise_percent(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().empty:
        return s
    if s.dropna().quantile(0.9) <= 1.01:
        s = s * 100
    return s.where(s >= 0)


def _pick(columns, patterns):
    lower = {c.lower(): c for c in columns}
    for p in patterns:
        if p.lower() in lower:
            return lower[p.lower()]
    for c in columns:
        lc = c.lower()
        if any(re.search(p, lc) for p in patterns if p.startswith("^")):
            return c
    return None


def parse_gpps(df: pd.DataFrame) -> pd.DataFrame:
    code = _pick(df.columns, ["practice_code", "prac_code"])
    name = _pick(df.columns, ["practice_name", "prac_name"])
    ics = _pick(df.columns, ["ics_name", "icb_name"])
    phone = _pick(df.columns, ["q1_12pct", "q1_1_2pct", r"^q1.*12pct$"])
    website = _pick(df.columns, ["q2_12pct", "q2_1_2pct", r"^q2.*12pct$"])
    app = _pick(df.columns, ["q3_12pct", "q3_1_2pct", r"^q3.*12pct$"])
    missing = [label for label, col in {"practice code": code, "practice name": name, "phone ease": phone}.items() if col is None]
    if missing:
        raise ValueError("GPPS columns not recognised: " + ", ".join(missing))
    out = pd.DataFrame({
        "practice_code": df[code].astype(str).str.strip(),
        "practice_name": df[name].astype(str).str.strip(),
        "ics_name": df[ics].astype(str).str.strip() if ics else "",
        "phone_easy_pct": _normalise_percent(df[phone]),
        "website_easy_pct": _normalise_percent(df[website]) if website else pd.NA,
        "app_easy_pct": _normalise_percent(df[app]) if app else pd.NA,
    })
    return out.drop_duplicates("practice_code")


def fetch_gpps(timeout=30) -> pd.DataFrame:
    r = requests.get(GPPS_URL, timeout=timeout)
    r.raise_for_status()
    return parse_gpps(pd.read_csv(io.BytesIO(r.content), low_memory=False))


def _find_download_link(page_url: str, text_fragment: str, timeout=30) -> str:
    r = requests.get(page_url, timeout=timeout)
    r.raise_for_status()
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
    out = pd.DataFrame({
        "practice_code": df[code].astype(str).str.strip(),
        "list_size": pd.to_numeric(df[n], errors="coerce"),
    })
    return out.dropna(subset=["list_size"]).drop_duplicates("practice_code")


def fetch_registered_patients(timeout=30) -> pd.DataFrame:
    url = _find_download_link(REGISTRATION_PAGE, "Totals (GP practice-all persons)", timeout=timeout)
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
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
