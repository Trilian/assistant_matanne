# core/planner.py
from core.helpers import log_function
from datetime import datetime, timedelta

class Planner:
    """Gestion des routines, tâches et rappels."""

    def __init__(self):
        self.tasks = []  # Liste des tâches : dict {name, module, task_name, datetime, done}
        self.routines = []  # Routines journalières ou hebdo

    @log_function
    def add_task(self, name, module, task_name, run_at=None):
        """Ajoute une tâche à la liste."""
        if run_at is None:
            run_at = datetime.now()
        task = {"name": name, "module": module, "task_name": task_name, "datetime": run_at, "done": False}
        self.tasks.append(task)
        return task

    @log_function
    def complete_task(self, name):
        """Marque une tâche comme terminée."""
        for task in self.tasks:
            if task["name"] == name:
                task["done"] = True
                return task
        return {"error": "Tâche non trouvée"}

    @log_function
    def get_pending_tasks(self):
        """Retourne les tâches non terminées et à exécuter."""
        now = datetime.now()
        return [t for t in self.tasks if not t["done"] and t["datetime"] <= now]

    @log_function
    def add_routine(self, name, module, task_name, schedule):
        """Ajoute une routine récurrente.
        schedule: dict avec clé 'daily', 'weekly', etc.
        """
        routine = {"name": name, "module": module, "task_name": task_name, "schedule": schedule}
        self.routines.append(routine)
        return routine

    @log_function
    def run_routines(self, orchestrator):
        """Exécute toutes les routines prévues pour maintenant."""
        now = datetime.now()
        results = []
        for r in self.routines:
            # Exemple simplifié : exécution quotidienne
            if "daily" in r["schedule"]:
                results.append(orchestrator.run_task(r["module"], r["task_name"]))
        return results
