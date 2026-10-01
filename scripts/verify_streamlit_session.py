from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90)
    app.run()
    if app.exception:
        messages = [str(item.value) for item in app.exception]
        raise RuntimeError("Streamlit session raised exceptions: " + " | ".join(messages))

    # The redesigned workspace should render the operator-first landing page.
    markdown_text = "\n".join(str(item.value) for item in app.markdown)
    assert "Today’s work queue" in markdown_text, "Operator work queue did not render"
    print("STREAMLIT SESSION OK: operator workspace rendered without exceptions")


if __name__ == "__main__":
    main()
