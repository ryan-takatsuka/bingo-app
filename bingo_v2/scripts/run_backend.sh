#!/bin/bash
# Script to run the Flask backend with conda environment

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# Source conda
source ~/miniforge3/etc/profile.d/conda.sh

# Activate conda environment
conda activate bingo-app

# Set Flask app
export FLASK_APP=app.py

# Run Flask
flask run --port=5001