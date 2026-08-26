"""账号凭据加密存储。

游戏账号密码使用 Fernet 对称加密后写入数据库。
密钥来自 MHXY_CREDENTIAL_KEY；开发环境未配置时，从 Django SECRET_KEY 派生稳定密钥。
API 层永远不返回明文密码，只有实际登录执行器在需要登录时显式解密。
"""
import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet() -> Fernet:
    configured = os.getenv("MHXY_CREDENTIAL_KEY", "").strip()
    if configured:
        try:
            return Fernet(configured.encode("utf-8"))
        except Exception as exc:
            raise RuntimeError("MHXY_CREDENTIAL_KEY 不是有效的 Fernet 密钥") from exc
    # 仅用于开发环境；生产环境应显式设置 MHXY_CREDENTIAL_KEY。
    derived = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest())
    return Fernet(derived)


def encrypt_password(password: str) -> str:
    if not password:
        return ""
    return _fernet().encrypt(password.encode("utf-8")).decode("utf-8")


def decrypt_password(ciphertext: str) -> str:
    if not ciphertext:
        return ""
    try:
        return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("账号密码无法解密，请检查 MHXY_CREDENTIAL_KEY 是否与写入时一致") from exc
