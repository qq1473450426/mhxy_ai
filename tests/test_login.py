import json

from engine.login import LoginLayout


def test_login_layout_from_env(monkeypatch):
    monkeypatch.setenv('MHXY_LOGIN_LAYOUT_JSON', json.dumps({
        'account': {'x': 10, 'y': 20},
        'password': {'x': 30, 'y': 40},
        'login': {'x': 50, 'y': 60},
    }))
    layout = LoginLayout.from_env()
    assert layout.account == (10, 20)
    assert layout.password == (30, 40)
    assert layout.login == (50, 60)
