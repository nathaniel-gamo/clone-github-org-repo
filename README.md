# Clone GitHub Organization Repositories

Clone repositories of your GitHub Organization!

## Installation

### Create .env file.
```
LOG_FILE_PATH=app.log
MAX_RETRIES=3
RETRY_INTERVAL_SECONDS=0
RETRY_RAISE_EXCEPTION=True
DESTINATION_FOLDER_NAME=Cloned Repositories (TSI)
```

### Create virtual environment.
```bash
python -m venv .venv
```

### Activate virtual environment.
```bash
.venv\Scripts\Activate.ps1
```

### Update pip.
```bash
python -m pip install -U pip
```

### Install dependencies.
```bash
pip install -r requirements.txt
```