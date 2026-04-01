"""Tests ciblés D10 pour modules cron extraits (jobs_schedule, jobs_phase_d)."""

from __future__ import annotations

from unittest.mock import MagicMock


def test_jobs_schedule_inclut_jobs_phase_d() -> None:
    from src.services.core.cron.jobs_schedule import configurer_jobs_planifies

    mock_planifier = MagicMock()
    configurer_jobs_planifies(mock_planifier)

    ids = [call.args[0] for call in mock_planifier.call_args_list]
    assert "rappels_jardin_saisonniers" in ids
    assert "verification_sante_systeme" in ids
    assert "backup_auto_hebdo_json" in ids
    assert "prediction_courses_weekly" in ids


def test_jobs_phase_d_backup_rotation_sans_exception(tmp_path, monkeypatch) -> None:
    from src.services.core.cron import jobs_phase_d

    class _FakeSession:
        def execute(self, _):
            class _Result:
                def mappings(self):
                    class _M:
                        def all(self):
                            return []

                    return _M()

            return _Result()

    class _Ctx:
        def __enter__(self):
            return _FakeSession()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.chdir(tmp_path)

    def _fake_db_ctx():
        return _Ctx()

    monkeypatch.setattr("src.core.db.obtenir_contexte_db", _fake_db_ctx)

    jobs_phase_d.executer_job_backup_auto_hebdo_json()

    backups = list((tmp_path / "data" / "exports" / "backup_auto").glob("backup_*.json"))
    assert len(backups) == 1
