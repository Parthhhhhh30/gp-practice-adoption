from data_pipeline import fetch_gpps, fetch_registered_patients


def main() -> None:
    gpps = fetch_gpps(timeout=45)
    assert len(gpps) > 5000, f"Unexpected GPPS row count: {len(gpps)}"
    required = {"practice_code", "practice_name", "phone_easy_pct", "website_easy_pct", "app_easy_pct"}
    missing = required.difference(gpps.columns)
    assert not missing, f"Missing GPPS columns: {sorted(missing)}"
    assert gpps["practice_code"].notna().all()
    assert gpps["phone_easy_pct"].notna().mean() > 0.90
    assert gpps["website_easy_pct"].notna().mean() > 0.90
    assert gpps["app_easy_pct"].notna().mean() > 0.90
    print(f"GPPS CORE OK: {len(gpps):,} practices")

    # Registered-patient totals are an optional enrichment. NHS England's publication
    # page can return HTTP 403 to automated cloud runners, while the GPPS core feed
    # remains directly accessible. The application already degrades safely to a null
    # list-size field; failure here must not invalidate the verified core public data.
    try:
        registered = fetch_registered_patients(timeout=45)
    except Exception as exc:
        print(f"OPTIONAL LIST-SIZE ENRICHMENT UNAVAILABLE: {type(exc).__name__}: {exc}")
        return

    assert len(registered) > 5000, f"Unexpected registered-patient row count: {len(registered)}"
    assert registered["list_size"].notna().all()
    assert (registered["list_size"] > 0).mean() > 0.99
    print(f"REGISTERED PATIENTS OK: {len(registered):,} practices")


if __name__ == "__main__":
    main()
