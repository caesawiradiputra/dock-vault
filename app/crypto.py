import base64

from configs.config import CONFIG_PATH
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class CryptoManager:
    def __init__(self, master_key):
        self.salt_path = CONFIG_PATH.parent / "salt.bin"
        self.load_or_create_salt()

        self.key = scrypt(
            master_key.encode(), salt=self.salt, key_len=32, N=2**14, r=8, p=1
        )

    def load_or_create_salt(self):
        if self.salt_path.exists():
            with open(self.salt_path, "rb") as f:
                self.salt = f.read()
        else:
            self.salt = get_random_bytes(32)
            with open(self.salt_path, "wb") as f:
                f.write(self.salt)

    def encrypt(self, data):
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=iv)
        ciphertext, tag = cipher.encrypt_and_digest(pad(data.encode(), AES.block_size))
        return base64.b64encode(iv + tag + ciphertext).decode()

    def decrypt(self, encrypted_data):
        decoded = base64.b64decode(encrypted_data.encode())
        iv = decoded[:16]
        tag = decoded[16:32]
        ciphertext = decoded[32:]

        cipher = AES.new(self.key, AES.MODE_GCM, nonce=iv)
        try:
            decrypted = unpad(
                cipher.decrypt_and_verify(ciphertext, tag), AES.block_size
            )
            return decrypted.decode()
        except (ValueError, KeyError):
            raise ValueError("Invalid decryption key or corrupted data")
