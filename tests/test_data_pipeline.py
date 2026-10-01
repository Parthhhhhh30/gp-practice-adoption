import pandas as pd
from data_pipeline import parse_gpps, parse_registered_patients


def test_parse_gpps_common_shape():
    df = pd.DataFrame({
        "practice_code": ["A1"], "practice_name": ["Demo"], "ics_name": ["London"],
        "q1_12pct": [.45], "q2_12pct": [.62], "q3_12pct": [.71],
    })
    out = parse_gpps(df)
    assert out.loc[0,"phone_easy_pct"] == 45
    assert out.loc[0,"app_easy_pct"] == 71


def test_parse_registered_patients():
    df = pd.DataFrame({"CODE":["A1"], "NUMBER_OF_PATIENTS":[12345]})
    out = parse_registered_patients(df)
    assert out.loc[0,"list_size"] == 12345
