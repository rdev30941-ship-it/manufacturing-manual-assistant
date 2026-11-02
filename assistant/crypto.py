import base64, hashlib
from cryptography.fernet import Fernet
from django.conf import settings

def _fernet():
    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))

def encrypt_secret(value):
    return _fernet().encrypt(value.encode()).decode() if value else ""

def decrypt_secret(value):
    return _fernet().decrypt(value.encode()).decode() if value else ""
