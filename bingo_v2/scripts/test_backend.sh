#!/bin/bash
# Script to test the Flask backend with conda environment

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# Source conda
source ~/miniforge3/etc/profile.d/conda.sh

# Activate conda environment
conda activate bingo-app

# Run tests
python -m pytest tests/ -v