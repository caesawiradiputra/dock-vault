# DockVault

DockVault is a secure, self-hosted credential management system designed for local use, with full encryption, a web-based interface, and Docker support.

## Features

- AES-256 encryption for all credentials  
- Master password protection  
- Web-based UI for managing credentials  
- Docker container support (recommended)  
- Import/export encrypted credential files  
- Cross-platform: Windows / Linux / Mac  
- SSH key passphrase support  
- Environment-based organization (prod/dev/staging)

## Installation

### Prerequisites

- Python 3.9+  
- Docker (optional but recommended)

### Method 1: Docker (Recommended)

```bash
docker build -t dock-vault .
docker run -d -p 5000:5000 -v ./data:/app/data dock-vault
```

### Method 2: Manual Setup

Clone the repository:

```bash
git clone https://github.com/yourusername/dockv-ault.git
cd dockvault
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

## Usage

Visit [http://localhost:5000](http://localhost:5000) in your browser.

### First Run
- Set your master password
- Start adding credentials

### Add Credentials
- Name / Type / Environment
- Username / Password
- JSON configuration
- Managed through the web interface

### Security Features
- All data is encrypted at rest
- Master password is never stored
- Session timeout after 30 minutes
- Encrypted `.enc` export files

### Backup & Restore

#### Export
- Click "Export" in the UI
- Set a passphrase
- Save the encrypted `.enc` file

#### Import
- Click "Import"
- Select the file
- Enter the correct passphrase

### File Structure
```
dock-vault/
├── app/                # Application code
│   ├── static/         # Static assets
│   ├── templates/      # HTML templates
│   ├── __init__.py     # Flask app factory
│   ├── auth.py         # Authentication
│   ├── crypto.py       # Encryption
│   ├── models.py       # Data models
│   └── routes.py       # API routes
├── configs/            # Application configs
│   ├── config.py       # Configuration
│   ├── logging.py      # Logging config
├── docker-compose.yml  # Docker config
├── Dockerfile          # Docker setup
├── requirements.txt    # Dependencies
└── main.py              # Entry point
```

## Troubleshooting

### Dialog too long?
- Zoom out in browser (Ctrl + -)
- Maximize your window

### Import fails?
- Check your passphrase
- Verify file integrity

### Docker issues?
```bash
chmod -R 700 ./data  # Fix file permission issues on volume
```

## License
MIT License
Feel free to use, modify, and distribute.

## Maintained By
[caesawiradiputra](https://github.com/caesawiradiputra)