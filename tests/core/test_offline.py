"""
Tests pour src/core/offline.py
Couvre :
- OperationEnAttente
- StatutConnexion
- TypeOperation
- Fonctions de queue offline
"""
import pytest
from unittest.mock import patch
from datetime import datetime
from src.core.offline import OperationEnAttente, StatutConnexion, TypeOperation

def test_pending_operation_to_dict():
    op = OperationEnAttente(model_name="Test", data={"a": 1}, operation_type=TypeOperation.UPDATE)
    d = op.to_dict()
    assert d["model_name"] == "Test"
    assert d["operation_type"] == TypeOperation.UPDATE
    assert isinstance(d["created_at"], str)
    assert d["data"] == {"a": 1}

def test_connection_status_enum():
    assert StatutConnexion.ONLINE == "online"
    assert StatutConnexion.OFFLINE == "offline"
    assert StatutConnexion.CONNECTING == "connecting"
    assert StatutConnexion.ERROR == "error"

def test_operation_type_enum():
    assert TypeOperation.CREATE == "create"
    assert TypeOperation.UPDATE == "update"
    assert TypeOperation.DELETE == "delete"
