import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from confirm_guard import request_confirm, ConfirmationDenied

def test_confirm_auto_approve(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    result = request_confirm("publish post to weibo")
    assert result["confirmed"] is True

def test_confirm_auto_deny(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    import pytest
    with pytest.raises(ConfirmationDenied):
        request_confirm("delete all drafts")
