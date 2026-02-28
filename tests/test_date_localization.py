from datetime import date

from src.core.date_utils.formatage import formater_date_fr


def test_formater_date_fr_contains_french_weekday():
    d = date(2026, 2, 28)  # 2026-02-28 is a samedi
    s = formater_date_fr(d, avec_annee=False)
    assert "samedi" in s.lower()
