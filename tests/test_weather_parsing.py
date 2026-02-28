from src.services.integrations.weather.types import MeteoJour


def test_uv_index_float_parsing():
    payload = {
        "date": "2026-02-28",
        "temperature_min": 2.0,
        "temperature_max": 8.5,
        "temperature_moyenne": 5.0,
        "humidite": 60,
        "precipitation_mm": 0.0,
        "probabilite_pluie": 10,
        "vent_km_h": 5.0,
        "direction_vent": "N",
        "uv_index": 5.5,
    }

    mj = MeteoJour.parse_obj(payload)
    assert isinstance(mj.uv_index, float)
    assert mj.uv_index == 5.5
