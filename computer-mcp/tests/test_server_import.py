import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_server_imports_without_error():
    import importlib
    mod = importlib.import_module("server")
    assert hasattr(mod, "mcp")
