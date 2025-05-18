# Conda Environment Setup for Bingo App V2

## Overview
This project uses a conda environment named `bingo-app` with Python 3.12 instead of virtualenv.

## Environment Setup

### Creating the Environment (if needed)
If the `bingo-app` environment doesn't exist:
```bash
conda create -n bingo-app python=3.12
```

### Activating the Environment
```bash
conda activate bingo-app
```

### Installing Dependencies
```bash
cd bingo_v2/backend
pip install -r requirements.txt
pip install pytest  # For testing
```

## Using Provided Scripts

The project includes several convenience scripts that handle conda activation automatically:

### Start Both Servers
```bash
cd bingo_v2
./scripts/start_app.sh
```

### Run Backend Only
```bash
cd bingo_v2
./scripts/run_backend.sh
```

### Run Tests
```bash
cd bingo_v2
./scripts/test_backend.sh
```

## Manual Commands

If you prefer to run commands manually:

### Backend Development
```bash
conda activate bingo-app
cd bingo_v2/backend
export FLASK_APP=app.py
flask run --port=5001
```

### Running Tests
```bash
conda activate bingo-app
cd bingo_v2/backend
python -m pytest tests/ -v
```

## Troubleshooting

### "conda: command not found"
Make sure conda is in your PATH. You may need to run:
```bash
source ~/miniforge3/etc/profile.d/conda.sh
```

### "ModuleNotFoundError"
Make sure you've activated the conda environment and installed all dependencies:
```bash
conda activate bingo-app
pip install -r requirements.txt
```

### Port Already in Use
The scripts use specific ports:
- Backend: 5001
- Frontend: 3001

If these ports are in use, you'll need to modify the scripts or use different ports.

## Notes
- The environment uses Python 3.12
- All Python dependencies are managed with pip within the conda environment
- Frontend dependencies are managed with npm (no conda needed)