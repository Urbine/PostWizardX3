# 🧙‍♂️ PostWizardX3

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: TBD](https://img.shields.io/badge/License-TBD-blue.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A comprehensive Python-based SEO toolset featuring machine learning classification, content optimization, and workflow
automation for WordPress-based content publishing pipelines.

## 📌 Project Overview

PostWizardX3 is a powerful automation tool that streamlines the process of creating, managing, and publishing content for WordPress-based affiliate marketing, with a focus on partner offers. The system combines content management with machine learning to optimize and automate the content pipeline.

PostWizardX3 is a robust suite of tools for webmasters and content managers, leveraging machine learning and
natural language processing for automated content classification and optimization.

## 🌟 Key Features

### 🎯 Content Management
- **Automated Post Creation**: Streamlined WordPress post generation
- **Taxonomy Management**: Intelligent category and tag handling
- **Batch Processing**: Handle multiple content items efficiently
- **Asset Management**: Automatic thumbnail and media handling
- **SEO Optimization**: Built-in tools for content optimization


### Machine Learning Classification System

- Multi-model classification approach using:
    - NLTK NaiveBayes Classifier
    - NLTK Maxent Classifier
    - Scikit-learn Multinomial NaiveBayes
- Automated content categorization
- Further model training possible from user feedback and WordPress site cache

### 🤖 Machine Learning
- **Multi-model Classification**:
  - NLTK NaiveBayes Classifier
  - NLTK Maxent Classifier
  - Scikit-learn Multinomial NaiveBayes
- **Continuous Learning**: Improves from user feedback and site data
- **Content Analysis**: Automatic/Interactive categorization



### ⚙️ Workflow Automation
- **Interactive & Headless Modes**: Flexible operation options
- **Content Synchronization**: Keeps local cache in sync with WordPress
- **Error Handling**: Robust retry mechanisms and logging
- **Progress Tracking**: Real-time monitoring of operations

### 🔄 Integration Ecosystem
- **WordPress REST API (Custom Wrapper)**: Seamless content publishing
- **Social Media**: Direct posting to X/Twitter and Telegram
- **Content Sources**: Support for multiple content providers
- **Search Integration**: Yandex and Brave Search API support

## Technical Requirements
- Python 3.11+
- Virtual environment support
- Required external services:
    - WordPress installation
    - ImageMagick (optional)
    - PostWizardREST API (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Urbine/PostDirectorX3.git
   cd PostDirectorX3
   ```

2. **Set up the environment**
   ```bash
   # Install UV if not already installed
   pip install uv
   
   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -e .
   ```

3. **Configure the application**
   ```bash
   # Launch configuration wizard
   python3 -m core.views.workflow_tweaks
   
   # Set up API keys and secrets
   python3 -m core.views.secret_mgr_view
   ```

## 🏗️ Project Structure

```
PostWizardX3/
├── core/               # Core functionality and utilities
│   ├── config/         # Configuration management
│   ├── controllers/    # Application controllers
│   ├── models/         # Data models
│   └── utils/          # Utility functions
│
├── flows/              # Main workflow implementations
│   ├── content_bot.py    # Content processing workflow
│   ├── gallery_bot.py    # Gallery management
│   └── feed_updater.py        # Content updates
│
├── integrations/       # Third-party integrations
├── ml_engine/          # Machine learning models and training
├── postwizard_sdk/     # PostWizardREST SDK components
├── wordpress/          # WordPress-specific functionality
└── workflows/          # Workflow definitions and management
```

## Usage

### Training Models
Before using the classification features, models need to be trained:

``` bash
python3 -m ml_engine.model_train

```

### Content Classification
``` python
from ml_engine.classifiers import classify_title, classify_description, classify_tags

# Classify content
title_categories = classify_title("Your content title")
desc_categories = classify_description("Your content description")
tag_categories = classify_tags("tag1, tag2, tag3")
```

## ⚙️ Configuration

### Using the Configuration Wizard

```bash
# Launch interactive configuration
python3 -m core.views.workflow_tweaks

# Manage API keys and secrets
python3 -m core.views.secret_mgr_view
```

### Main Configuration Files
- `pyproject.toml` - Project metadata and dependencies
- `workflows_config.ini` - Workflow configurations
- `.python-version` - Python version specification


## 🧪 Testing

Run the full test suite:
```bash
./scripts/run_all_tests.sh .
```

## 🧹 Code Quality

This project uses `ruff` for linting and formatting:

```bash
# Check code style
ruff check .

# Format code
ruff format .
```

## License
TDB - see the LICENSE file for details.

## ✉️ Contact

For questions or support, please contact:
- **Yoham Gabriel**
- Email: yohamg@programmer.net
- GitHub: [@Urbine](https://github.com/Urbine)
This project is under active development. Features and documentation are continuously being improved and updated.
---

> Built with ❤️ by [Yoham Gabriel](https://github.com/Urbine) | [Report an issue](https://github.com/Urbine/PostDirectorX3/issues)