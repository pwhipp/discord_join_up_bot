#!/bin/bash

# Change to the directory this script is in
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

# Activate the virtual environment
source venv/bin/activate

# Run the bot module
python -m join_up_bot


