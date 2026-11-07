"""Tests for the public evidence boundary and interactive landing decisions."""
import pandas as pd
import pytest

from story import decision_feedback, story_stats

@pytest.mark.parametrize("lens,correct",[
    ("Public access","Check the practice's workflow before treating the access result as a product opportunity"),
    ("Rollout risk","Resolve the open support and activation blocker before discussing expansion"),
    ("Customer feedback","Record the exact issue, evidence and owner for human review"),
])
def test_supported_decision(lens,correct):
    assert decision_feedback(lens,correct)[0] is True
    assert decision_feedback(lens,"Automatically send customer email")[0] is False

def test_unknown_decision_never_falls_through():
    with pytest.raises(ValueError):
        decision_feedback("Clinical diagnosis","anything")

def test_public_data_unavailable_is_not_fabricated():
    n,m,d=story_stats(pd.DataFrame(columns=["phone_easy_pct"]),pd.DataFrame({"id":[1,2]}))
    assert (n,m,d)==("—","—","02")

def test_real_context_counts_use_input_data():
    p=pd.DataFrame({"phone_easy_pct":[60,80,90]})
    n,m,d=story_stats(p,p.iloc[:2])
    assert (n,m,d)==("3","80%","02")
