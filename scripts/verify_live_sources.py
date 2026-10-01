from data_pipeline import fetch_gpps, fetch_registered_patients


def main() -> None:
    gpps = fetch_gpps(timeout=45)
    assert len(gpps) > 5000, f"Unexpected GPPS row count: {len(gpps)}"
    required = {"practice_code", "practice_name", "phone_easy_pct", "website_easy_pct", "app_easy_pct"}
    missing = required.difference(gpps.columns)
    assert not missing, f"Missing GPPS columns: {sorted(missing)}"
    assert gpps["practice_code"].notna().all()
    assert gpps["phone_easy_pct"].notna().mean() > 0.90
    print(f"GPPS OK: {len(gpps):,} practices")

    registered = fetch_registered_patients(timeout=45)
    assert len(registered) > 5000, f"Unexpected registered-patient row count: {len(registered)}"
    assert registered["list_size"].notna().all()
    assert (registered["list_size"] > 0).mean() > 0.99
    print(f"Registered patients OK: {len(registered):,} practices")


if __name__ == "__main__":
    main()
