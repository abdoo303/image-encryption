#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Build frontend
cd frontend
npm install
npm run build
cd ..

echo "Build completed successfully!"
