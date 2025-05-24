# webmaster-seo-tools

A comprehensive Python-based SEO toolset featuring machine learning classification, content optimization, and workflow
automation.

## Overview

This project provides a robust suite of tools for webmasters and content managers, leveraging machine learning and
natural language processing for automated content classification and optimization.

## Core Features

### Machine Learning Classification System

- Multi-model classification approach using:
    - NLTK NaiveBayes Classifier
    - NLTK Maxent Classifier
    - Scikit-learn Multinomial NaiveBayes
- Automated content categorization
- Smart tag suggestions
- Continuous learning from user feedback

### Content Management Tools

- Automated title and description analysis
- Tag optimization and categorization
- Content embedding assistance
- SEO optimization workflows

### Integration Support

- WordPress API integration
- Social media posting (X/Twitter, Telegram)
- Multiple data source handling
- External API support (Yandex, Brave Search)

## Technical Requirements

- Python 3.13.3+
- Virtual environment support
- Required external services:
    - WordPress installation
    - ImageMagick (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/webmaster-seo-tools.git
cd webmaster-seo-tools
```

### Setting Up UV Package Manager

This project uses UV for dependency management. To set up UV:

```bash
# Install UV
pip install uv

# Create a new virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt
```

## Project Structure

webmaster-seo-tools/
├── core/               # Core functionality and utilities
├── docs/              # Documentation
├── logs/              # Application logs
├── ml_engine/         # Machine learning models and training
│   ├── ml_models/     # Trained model files
│   └── model_train/   # Training scripts and utilities
├── setup/             # Setup and configuration scripts
├── tasks/             # Task definitions and scheduling
├── tests/             # Test suite
├── scripts/           # Utility scripts
├── workflows/         # Main application workflows
└── experimental/      # Experimental features and testing      # Utility scripts

## Usage

### Training Models
Before using the classification features, models need to be trained:

``` python
from ml_engine.model_train import train_models

# Train all models
train_models()
```

### Content Classification
``` python
from ml_engine.classifiers import classify_title, classify_description, classify_tags

# Classify content
title_categories = classify_title("Your content title")
desc_categories = classify_description("Your content description")
tag_categories = classify_tags("tag1, tag2, tag3")
```

## Configuration

The project uses a configuration management system located in `core/config/`. Modify the configuration files to adjust:

- Model parameters
- Classification thresholds
- Logging settings
- Integration parameters

The project uses various configuration files:

- Project metadata and dependencies: `pyproject.toml`
- Python version specification: `.python-version`
- Python package dependencies: `requirements.txt`

### Running Tests
``` bash
python -m pytest tests/
```

### Code Style
This project follows PEP 8 guidelines and uses ruff for linting:
``` bash
ruff check .
```

## Documentation
Detailed documentation is available in the directory. Key documentation includes: `docs/`
- API Reference
- Machine Learning Model Specifications
- Workflow Guides
- Integration Examples

## License
TDB - see the LICENSE file for details.

## Author
Yoham Gabriel B. @Urbine
- GitHub: [@YohamGabriel](https://github.com/YohamGabriel)
- Email: yohamg@programmer.net

## Status
This project is under active development. Features and documentation are continuously being improved and updated.
For more information, bug reports, or feature requests, please open an issue on the GitHub repository.
