from engine.credential_store import decrypt_password, encrypt_password
from engine.reconnect import ReconnectCoordinator, ReconnectPolicy, ReconnectState


def test_password_is_reversible_but_not_plaintext():
    raw = '测试密码-123'
    encrypted = encrypt_password(raw)
    assert encrypted != raw
    assert decrypt_password(encrypted) == raw


class FakeExecutor:
    def __init__(self): self.reconnect_calls = 0; self.switch_calls = 0
    def reconnect(self, account_id, password=None):
        self.reconnect_calls += 1
        return {'success': self.reconnect_calls >= 2}
    def switch_account(self, failed_account_id, backup_account_id):
        self.switch_calls += 1
        return {'success': True}


def test_reconnect_then_backup_switch():
    executor = FakeExecutor()
    coordinator = ReconnectCoordinator(executor, ReconnectPolicy(max_attempts=2, max_backup_switches=1))
    state = ReconnectState(1, active_account_id=1)
    first = coordinator.handle_disconnect(state, [2])
    assert first['status'] == 'RETRY'
    second = coordinator.handle_disconnect(state, [2])
    assert second['status'] == 'RECONNECTED'
