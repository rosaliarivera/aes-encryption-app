import os
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

backend = default_backend()

def derive_key(password: str, key_bits: int, salt: bytes = None) -> (bytes, bytes):
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_bits // 8,
        salt=salt,
        iterations=100_000,
        backend=backend
    )
    key = kdf.derive(password.encode('utf-8'))
    return key, salt

def pad(data: bytes) -> bytes:
    padder = padding.PKCS7(128).padder()
    return padder.update(data) + padder.finalize()

def unpad(padded: bytes) -> bytes:
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()

def encrypt(plaintext: str, password: str, mode: str, key_bits: int) -> str:
    mode = mode.upper()
    key, salt = derive_key(password, key_bits)
    iv = None
    data = plaintext.encode('utf-8')

    if mode in ('ECB', 'CBC'):
        data = pad(data)

    if mode == 'ECB':
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(data) + encryptor.finalize()
    elif mode == 'CBC':
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(data) + encryptor.finalize()
    elif mode == 'CFB':
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(data) + encryptor.finalize()
    else:
        raise ValueError('Modo no soportado')

    payload = {
        'mode': mode,
        'key_bits': key_bits,
        'salt': base64.b64encode(salt).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8') if iv is not None else None,
        'ciphertext': base64.b64encode(ct).decode('utf-8')
    }
    return json.dumps(payload)

def decrypt(payload_json: str, password: str) -> str:
    obj = json.loads(payload_json)
    mode = obj['mode']
    key_bits = int(obj['key_bits'])
    salt = base64.b64decode(obj['salt'])
    iv = base64.b64decode(obj['iv']) if obj.get('iv') else None
    ct = base64.b64decode(obj['ciphertext'])

    key, _ = derive_key(password, key_bits, salt=salt)

    if mode == 'ECB':
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
        decryptor = cipher.decryptor()
        pt_p = decryptor.update(ct) + decryptor.finalize()
        pt = unpad(pt_p)
    elif mode == 'CBC':
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        pt_p = decryptor.update(ct) + decryptor.finalize()
        pt = unpad(pt_p)
    elif mode == 'CFB':
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        decryptor = cipher.decryptor()
        pt = decryptor.update(ct) + decryptor.finalize()
    else:
        raise ValueError('Modo no soportado')

    return pt.decode('utf-8')
