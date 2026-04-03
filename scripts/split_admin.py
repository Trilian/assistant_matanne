"""
Script to split admin.py (3769 lines) into domain-specific modules.

Split plan:
- admin_shared.py: Rate limiting, helpers, schemas, constants (~670 lines)
- admin_audit.py: Audit + Events endpoints (lines 139-502) 
- admin_jobs.py: Jobs constants + helpers + endpoints (lines 631-2025)
- admin_operations.py: Services Health + Notifications + IA + Cache + Users (lines 2026-2617)
- admin_infra.py: DB + Dashboard + Actions + Config + Console + Resync + Seed + Reset + Logs (lines 2618-3769)
- admin.py: Thin re-export for backward compat (est_mode_test_actif, _resumer_api_metrics)
"""

import os


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Created {path} ({content.count(chr(10))+1} lines)")


lines = read_file("src/api/routes/admin.py")
print(f"Read {len(lines)} lines from admin.py")


# Helper to extract text from line range (1-indexed inclusive)
def extract(start, end):
    return "".join(lines[start - 1 : end])


# ═══════════════════════════════════════════════════════════════════════════════
# FILE 1: admin_shared.py
# Contains: rate limiting deps, router, log helpers, ALL schemas, ALL constants,
#           ALL helper functions
# ═══════════════════════════════════════════════════════════════════════════════
shared = '''"""
Module partagé pour les routes admin.

Contient les dépendances, schémas, constantes et helpers utilisés
par tous les sous-modules admin.
"""

from __future__ import annotations

import collections
import csv
import io
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import text

from src.api.dependencies import require_auth, require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

'''

# Rate limiting admin (lines 55-84)
shared += extract(55, 84)
shared += "\n"
# Rate limiting jobs (lines 86-104)
shared += extract(86, 104)
shared += "\n"
# Router + log helpers (lines 106-138)
shared += extract(106, 138)
# Schemas (lines 503-630)
shared += "\n" + extract(503, 630)
# JOBS constants (lines 631-730)
shared += "\n" + extract(631, 730)
# Helper functions (lines 731-1173)
shared += "\n" + extract(731, 1173)

write_file("src/api/routes/admin_shared.py", shared)

# ═══════════════════════════════════════════════════════════════════════════════
# FILE 2: admin_audit.py
# Audit logs + Events endpoints
# ═══════════════════════════════════════════════════════════════════════════════
audit = '''"""Routes admin — Audit et Events."""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import text

from src.api.dependencies import require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    _construire_pdf_audit,
    _journaliser_action_admin,
    _verifier_limite_admin,
    router,
)

logger = logging.getLogger(__name__)

'''

# Audit + Events endpoints (lines 139-502)
audit += extract(139, 502)

write_file("src/api/routes/admin_audit.py", audit)

# ═══════════════════════════════════════════════════════════════════════════════
# FILE 3: admin_jobs.py
# Bridges status + Jobs endpoints
# ═══════════════════════════════════════════════════════════════════════════════
jobs = '''"""Routes admin — Jobs et Bridges."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from src.api.dependencies import require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    JobInfoResponse,
    JobsBulkRequest,
    JobsSimulationJourneeRequest,
    _LABELS_JOBS,
    _ajouter_log_job,
    _extraire_jobs_matin,
    _job_logs,
    _job_trigger_timestamps,
    _journaliser_action_admin,
    _verifier_limite_admin,
    _verifier_limite_jobs,
    router,
)

logger = logging.getLogger(__name__)

'''

# Jobs endpoints (lines 1174-2025)
jobs += extract(1174, 2025)

write_file("src/api/routes/admin_jobs.py", jobs)

# ═══════════════════════════════════════════════════════════════════════════════
# FILE 4: admin_operations.py
# Services Health + Notifications + IA + Cache + Users
# ═══════════════════════════════════════════════════════════════════════════════
ops = '''"""Routes admin — Opérations (Services, Notifications, IA, Cache, Utilisateurs)."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from src.api.dependencies import require_auth, require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    CachePurgeRequest,
    CacheStatsResponse,
    NotificationTestRequest,
    UtilisateurAdminResponse,
    _NOTIFICATION_TEMPLATES,
    _admin_timestamps,
    _journaliser_action_admin,
    _verifier_limite_admin,
    router,
)

logger = logging.getLogger(__name__)

'''

# Services Health + Notifications + IA + Cache + Users (lines 2026-2617)
ops += extract(2026, 2617)

write_file("src/api/routes/admin_operations.py", ops)

# ═══════════════════════════════════════════════════════════════════════════════
# FILE 5: admin_infra.py
# DB + Dashboard + Actions + Config + Console + Resync + Seed + Reset + Logs
# ═══════════════════════════════════════════════════════════════════════════════
infra = '''"""Routes admin — Infrastructure (DB, Config, Console, DevTools)."""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from src.api.dependencies import require_auth, require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    AdminQuickCommandRequest,
    ConfigAdminExportRequest,
    ConfigAdminImportRequest,
    DbExportRequest,
    DbImportRequest,
    FeatureFlagsUpdateRequest,
    FlowSimulationRequest,
    ResetModuleRequest,
    RuntimeConfigUpdateRequest,
    _FEATURE_FLAGS_PAR_DEFAUT,
    _LABELS_JOBS,
    _MODULES_RESETABLES,
    _NAMESPACE_FEATURE_FLAGS,
    _NAMESPACE_RUNTIME_CONFIG,
    _RUNTIME_CONFIG_PAR_DEFAUT,
    _VUES_SQL_AUTORISEES,
    _admin_timestamps,
    _catalogue_actions_services,
    _cibles_resync,
    _ecrire_namespace_persistant,
    _exporter_config_admin,
    _executer_action_service,
    _importer_config_admin,
    _lire_namespace_persistant,
    _normaliser_nom_table,
    _parser_commande_rapide,
    _resumer_api_metrics,
    _serialiser_valeur_export_db,
    _simuler_flux_admin,
    _simuler_test_e2e_one_click,
    _verifier_limite_admin,
    est_mode_test_actif,
    _journaliser_action_admin,
    router,
)

logger = logging.getLogger(__name__)

'''

# DB + Dashboard + Actions + Config + Console + Resync + Seed + Reset + Logs (lines 2618-3769)
infra += extract(2618, 3769)

write_file("src/api/routes/admin_infra.py", infra)

# ═══════════════════════════════════════════════════════════════════════════════
# FILE 6: admin.py (thin backward-compat re-export)
# ═══════════════════════════════════════════════════════════════════════════════
reexport = '''"""
Routes d\'administration — point d\'entrée & rétro-compatibilité.

Le code a été réparti dans :
- admin_shared.py   : Schémas, constantes, helpers partagés
- admin_audit.py    : Audit logs & Events
- admin_jobs.py     : Jobs & Bridges
- admin_operations.py : Services, Notifications, IA, Cache, Utilisateurs
- admin_infra.py    : DB, Config, Console, DevTools, Seed, Reset

Ce fichier conserve les re-exports utilisés par d\'autres modules.
"""

# Re-exports consommés par d\'autres modules
from src.api.routes.admin_shared import (  # noqa: F401
    est_mode_test_actif,
    router,
    _resumer_api_metrics,
)

# Importer les sous-modules pour enregistrer les endpoints sur le router partagé
from src.api.routes import admin_audit as _audit  # noqa: F401
from src.api.routes import admin_jobs as _jobs  # noqa: F401
from src.api.routes import admin_operations as _ops  # noqa: F401
from src.api.routes import admin_infra as _infra  # noqa: F401

__all__ = ["router", "est_mode_test_actif", "_resumer_api_metrics"]
'''

write_file("src/api/routes/admin.py", reexport)

print("\nDone! Split complete.")
print("Files created:")
print("  - admin_shared.py (schemas, constants, helpers)")
print("  - admin_audit.py (audit + events)")
print("  - admin_jobs.py (jobs + bridges)")
print("  - admin_operations.py (services, notifications, IA, cache, users)")
print("  - admin_infra.py (DB, config, console, devtools)")
print("  - admin.py (thin re-export)")
