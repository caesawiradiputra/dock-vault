import os
import platform
from pathlib import Path


def main():
    system = platform.system()
    if system == "Windows":
        base_path = Path("D:/credential-manager-data")
        if not base_path.parent.exists():
            base_path = Path.home() / "credential-manager-data"
    else:
        base_path = Path.home() / "credential-manager-data"

    dirs = ["config", "data", "backups", "logs"]

    print(f"Setting up directories in: {base_path}")

    for dir_name in dirs:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

        if system != "Windows":
            dir_path.chmod(0o700)

    config_file = base_path / "config/config.ini"
    if not config_file.exists():
        config_file.write_text(
            """[security]
password_complexity = high
auto_backup = true

[logging]
level = INFO
"""
        )

    print("Setup complete. Data will be stored at:")
    print(base_path)


if __name__ == "__main__":
    main()
