import base64
import json
from datetime import datetime

from configs.config import BACKUP_PATH, DATA_PATH
from configs.logging import logger
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

from app.crypto import CryptoManager


class CredentialManager:
    SCHEMA_VERSION = 2

    def __init__(self, master_key, storage_path=DATA_PATH):
        self.crypto = CryptoManager(master_key)
        self.storage_path = storage_path
        self.credentials = []
        self.metadata = {
            "version": self.SCHEMA_VERSION,
            "created_at": datetime.now().isoformat(),
        }
        self.load_credentials()

    def load_credentials(self):
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                encrypted = f.read()
                decrypted = self.crypto.decrypt(encrypted)
                data = json.loads(decrypted)

                if isinstance(data, dict) and "credentials" in data:
                    self.credentials = data["credentials"]
                    self.metadata = data.get("metadata", {})
                else:
                    self.credentials = data

    def save_credentials(self):
        data = {
            "version": self.SCHEMA_VERSION,
            "metadata": self.metadata,
            "credentials": self.credentials,
            "updated_at": datetime.now().isoformat(),
        }
        encrypted = self.crypto.encrypt(json.dumps(data))
        with open(self.storage_path, "w") as f:
            f.write(encrypted)

    def add_credential(
        self, name, cred_type, env, username, secret, details=None, ssh_passphrase=None
    ):
        self.credentials.append(
            {
                "id": str(datetime.now().timestamp()),
                "name": name,
                "type": cred_type,
                "env": env,
                "username": username,
                "secret": secret,
                "ssh_passphrase": ssh_passphrase if cred_type == "ssh" else None,
                "details": details or {},
                "created_at": datetime.now().isoformat(),
            }
        )
        self.save_credentials()

    def update_credential(self, cred_id, **kwargs):
        for cred in self.credentials:
            if cred["id"] == cred_id:
                for k, v in kwargs.items():
                    if k in cred:
                        cred[k] = v
                cred["updated_at"] = datetime.now().isoformat()
                self.save_credentials()
                return True
        return False

    def delete_credential(self, cred_id):
        self.credentials = [c for c in self.credentials if c["id"] != cred_id]
        self.save_credentials()

    def get_credential(self, cred_id):
        return next((c for c in self.credentials if c["id"] == cred_id), None)

    def get_all_credentials(self):
        return self.credentials

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_PATH / f"backup_{timestamp}.dat"
        with open(backup_file, "w") as f:
            f.write(
                self.crypto.encrypt(
                    json.dumps(
                        {"credentials": self.credentials, "metadata": self.metadata}
                    )
                )
            )
        return backup_file

    def export_encrypted_data(self, passphrase):
        """Export encrypted data with passphrase"""
        data = {
            "version": self.SCHEMA_VERSION,
            "credentials": self.credentials,
            "metadata": self.metadata,
            "exported_at": datetime.now().isoformat(),
        }

        # Generate random salt
        salt = get_random_bytes(16)

        # Derive key from passphrase
        key = PBKDF2(passphrase, salt, dkLen=32, count=100000)

        # Encrypt data
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(json.dumps(data).encode())

        # Combine salt + ciphertext + tag
        encrypted_data = salt + cipher.nonce + tag + ciphertext

        # Return base64 encoded
        return base64.b64encode(encrypted_data).decode()

    def import_encrypted_data(self, encrypted_data, passphrase):
        """Import encrypted data with passphrase"""
        try:
            # Decode base64
            encrypted_data = base64.b64decode(encrypted_data)

            # Extract components
            salt = encrypted_data[:16]
            nonce = encrypted_data[16:32]
            tag = encrypted_data[32:48]
            ciphertext = encrypted_data[48:]

            # Derive key
            key = PBKDF2(passphrase, salt, dkLen=32, count=100000)

            # Decrypt
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)

            # Load data
            data = json.loads(decrypted)

            # Validate
            if not isinstance(data, dict) or "credentials" not in data:
                raise ValueError("Invalid decrypted data format")

            self.credentials = data["credentials"]
            self.metadata = data.get("metadata", {})
            self.save_credentials()
            return True

        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise ValueError("Invalid passphrase or corrupted data")
