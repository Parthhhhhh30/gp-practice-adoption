import pandas as pd

from data_pipeline import parse_gpps, parse_registered_patients


def test_parse_gpps_legacy_summary_shape():
    df = pd.DataFrame(
        {
            "practice_code": ["A1"],
            "practice_name": ["Demo"],
            "ics_name": ["London"],
            "q1_12pct": [.45],
            "q2_12pct": [.62],
            "q3_12pct": [.71],
        }
    )
    out = parse_gpps(df)
    assert out.loc[0, "phone_easy_pct"] == 45
    assert out.loc[0, "app_easy_pct"] == 71


def test_parse_gpps_2026_practice_shape_uses_easy_responses_2_and_3():
    df = pd.DataFrame(
        {
            "ad_practicecode": ["B2"],
            "ad_practicename": ["Current Demo"],
            "ad_icsname": ["Example ICS"],
            "localgpservicesphone_1.pct": [12.0],
            "localgpservicesphone_2.pct": [30.0],
            "localgpservicesphone_3.pct": [25.0],
            "localgpserviceswebsite_1.pct": [20.0],
            "localgpserviceswebsite_2.pct": [40.0],
            "localgpserviceswebsite_3.pct": [15.0],
            "localgpservicesapp_1.pct": [35.0],
            "localgpservicesapp_2.pct": [28.0],
            "localgpservicesapp_3.pct": [22.0],
        }
    )
    out = parse_gpps(df)
    assert out.loc[0, "practice_code"] == "B2"
    assert out.loc[0, "practice_name"] == "Current Demo"
    assert out.loc[0, "phone_easy_pct"] == 55
    assert out.loc[0, "website_easy_pct"] == 55
    assert out.loc[0, "app_easy_pct"] == 50


def test_parse_registered_patients():
    df = pd.DataFrame({"CODE": ["A1"], "NUMBER_OF_PATIENTS": [12345]})
    out = parse_registered_patients(df)
    assert out.loc[0, "list_size"] == 12345
