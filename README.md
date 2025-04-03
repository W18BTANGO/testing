# Testing Repository

This repository contains integration and end-to-end tests for the preprocessing and analytics services.

## Setup

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tests
```

## CI Pipeline

The CI pipeline automatically runs all tests and generates coverage reports which are uploaded as artifacts.