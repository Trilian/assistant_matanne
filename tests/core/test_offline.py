"""
Tests pour src/core/offline.py
Couvre :
- PendingOperation
- ConnectionStatus
- OperationType
- Fonctions de queue offline
"""
import pytest
from unittest.mock import patch
from datetime import datetime
from src.core.offline import PendingOperation, ConnectionStatus, OperationType

def test_pending_operation_to_dict():
    op = PendingOperation(model_name="Test", data={"a": 1}, operation_type=OperationType.UPDATE)
    d = op.to_dict()
    assert d["model_name"] == "Test"
    assert d["operation_type"] == OperationType.UPDATE
    assert isinstance(d["created_at"], str)
    assert d["data"] == {"a": 1}

def test_connection_status_enum():
    assert ConnectionStatus.ONLINE == "online"
    assert ConnectionStatus.OFFLINE == "offline"
    assert ConnectionStatus.CONNECTING == "connecting"
    assert ConnectionStatus.ERROR == "error"

def test_operation_type_enum():
    assert OperationType.CREATE == "create"
    assert OperationType.UPDATE == "update"
    assert OperationType.DELETE == "delete"
