#!/bin/bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate genai-desktop-client
python run_app.py
