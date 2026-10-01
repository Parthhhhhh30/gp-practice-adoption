from types import SimpleNamespace

from workspace import queue_item


def account(onboarding="Green", adoption="Green", upsell="Not ready"):
    return SimpleNamespace(
        onboarding_health=onboarding,
        adoption_health=adoption,
        upsell_state=upsell,
    )


def test_red_onboarding_enters_customer_risk_queue():
    item = queue_item(account(onboarding="Red", adoption="Green"))
    assert item is not None
    assert item["priority"] == 0
    assert item["label"] == "Customer risk"


def test_red_adoption_enters_customer_risk_queue():
    item = queue_item(account(onboarding="Green", adoption="Red"))
    assert item is not None
    assert item["priority"] == 0


def test_expansion_only_after_no_red_state():
    item = queue_item(account(onboarding="Green", adoption="Green", upsell="Ready for discovery"))
    assert item is not None
    assert item["priority"] == 1


def test_amber_onboarding_gets_check_in():
    item = queue_item(account(onboarding="Amber", adoption="Green"))
    assert item is not None
    assert item["priority"] == 2


def test_healthy_non_expansion_account_not_forced_into_queue():
    assert queue_item(account()) is None
