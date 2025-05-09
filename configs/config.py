import os
import platform
from pathlib import Path


def get_data_root():
    system = platform.system()
    if system == "Windows":
        # Try D: drive first, fall back to user directory
        d_drive = Path("D:/credential-manager-data")
        if d_drive.parent.exists():
            return d_drive
        return Path.home() / "credential-manager-data"
    else:  # Linux/Mac
        return Path.home() / "credential-manager-data"


DEBUG = os.getenv("DEBUG", "false").lower() == "true"

BASE_DIR = get_data_root()
CONFIG_PATH = BASE_DIR / "config/config.ini"
DATA_PATH = BASE_DIR / "data/credentials.dat"
BACKUP_PATH = BASE_DIR / "backups"
LOG_PATH = BASE_DIR / "logs"

# Ensure directories exist with proper permissions
for path in [CONFIG_PATH.parent, DATA_PATH.parent, BACKUP_PATH, LOG_PATH]:
    path.mkdir(parents=True, exist_ok=True)
    if platform.system() != "Windows":
        path.chmod(0o700)  # RWX for owner only on Unix
