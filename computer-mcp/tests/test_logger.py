import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from logger import ActionLogger

def test_log_action_returns_entry():
    log = ActionLogger(log_file=None)  # no file, in-memory only
    entry = log.record("click", {"x": 100, "y": 200})
    assert entry["tool"] == "click"
    assert entry["params"] == {"x": 100, "y": 200}
    assert "timestamp" in entry

def test_log_never_stores_password():
    log = ActionLogger(log_file=None)
    entry = log.record("type_text", {"text": "mypassword", "secret": True})
    assert entry["params"].get("text") == "[REDACTED]"
