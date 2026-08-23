# Clone GitHub Organization Repositories

Clone repositories from your GitHub organization using a Python CLI.

## Guide

### Create .env file.
```
MAX_RETRIES=0
RETRY_INTERVAL_SECONDS=0
RETRY_RAISE_EXCEPTION=True
DESTINATION_FOLDER_NAME=Cloned Repositories
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

### Install packages.
```bash
pip install -r requirements.txt
```

### Create executable file.
```bash
python -m nuitka main.py --onefile --windows-console-mode=force --remove-output --assume-yes-for-downloads --output-filename=clone-github-org-repo.exe --output-dir= "C:\Users\{User Profile}\Downloads"
```