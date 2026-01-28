# 🧙‍♂️ PostWizardX3

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](./LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **Archived Project: WordPress Content Management System with ML**
>
> PostWizardX3 is a feature-rich content management system designed for WordPress-based WordPress-based content publishing.
> It provides tools for automated content ingestion, machine learning classification, and publishing workflows.
>
> This project is no longer maintained but remains available as a reference implementation.

---

## 🚦 Project Status

**Status:** Archived / Not Maintained

This repository is preserved for reference and educational purposes only.

- ✅ Fully functional codebase with multiple integrated components
- ⚠️ No longer actively maintained or supported
- ⚠️ Dependencies may be outdated
- ❌ No security updates or bug fixes
- ❌ Not recommended for production use without significant updates

---

## 🎯 Key Features

- **Content Management**
  - Automated WordPress post creation and management
  - Video content processing and classification
  - Thumbnail management and asset handling

- **Machine Learning**
  - Content classification using scikit-learn
  - Natural language processing for content analysis
  - Model training and evaluation tools

- **Workflow Automation**
  - Batch processing of content
  - Automated artifact selection
  - Content synchronization

## 🛠️ Technical Stack

- **Language**: Python 3.11+
- **ML Stack**: scikit-learn, NLTK, NumPy, SciPy
- **Web**: aiohttp, requests, BeautifulSoup4
- **WordPress**: REST API integration
- **Build & Tools**: Ruff, uv

---

## 📌 Project Overview

PostWizardX3 is a comprehensive content management system designed for WordPress, with a focus on WordPress-based content publishing. It provides a complete pipeline for:
**content optimization and workflow orchestration**, the architectural patterns are broadly
applicable to automation-heavy publishing systems.

### What This Project Demonstrates

- End-to-end content automation workflows for WordPress-based sites
- Modular, bot-driven architectures for different content types
- Practical use of NLP-based classification in publishing pipelines
- Multi-source content ingestion and normalization
- Integration patterns for third-party APIs
- Configuration-driven extensibility with minimal hardcoding

### Original Context

This project was originally built as an internal tool for managing high-volume, automated
content publishing. The original product and service are no longer active, but the engineering
work remains valuable as:

- A **reference implementation** for similar automation systems
- A **learning resource** for complex workflow orchestration
- A **production-grade system** demonstrating architectural and integration patterns
- A **foundation** for experimentation or adaptation

---

## TL;DR

- 🏛️ Archived project, not currently maintained
- 🧠 Complete automation + ML-driven publishing system
- 🧩 Modular, bot-based architecture
- ⚠️ Requires updates for production use
- ❌ No guaranteed maintenance

---

## 🌟 Key Features

### 🤖 Machine Learning Classification

- Ensemble-based text classification using:
  - NLTK Naive Bayes
  - NLTK Maximum Entropy
  - Scikit-learn Multinomial Naive Bayes (TF-IDF)
- Category, tag, and description-based predictions
- Designed for large-scale, semi-automated publishing workflows
- Supports retraining using corrected classifications

### 📝 Content Management

- WordPress REST API integration with authentication handling
- Local caching for efficient synchronization
- Automated category, tag, and media management
- SQLite-based content repositories for ingestion and staging

### 🎬 Specialized Content Workflows

The system includes multiple **bot-style workflows**, each implementing a common interface:

- Video content automation
- Photo gallery automation
- Embed-based publishing
- Database synchronization and updating

These workflows are intended to demonstrate architectural and orchestration patterns rather
than serve as polished end-user tools.

### 🌐 External Integrations

- WordPress REST API
- Social platforms (X/Twitter, Telegram)
- Search APIs (multiple providers)
- Third-party media provider feeds

### 🔧 Configuration & Administration

- Interactive Gradio-based configuration UIs
- File-based configuration and secrets management
- Support for multiple authentication and API key types

---

## 🏗️ Architecture Overview

### Core Architectural Patterns

- **Factory Pattern** — configuration object creation
- **MVC-inspired separation** — models, controllers, and Gradio-based views
- **Strategy Pattern** — interchangeable content bot workflows
- **Adapter Pattern** — unified interfaces over third-party APIs
- **Builder Pattern** — payload and request construction

### 🏗️ Project Structure

```
PostWizardX3/
├── core/                          # Core framework and utilities
│   ├── config/                    # Configuration management
│   ├── controllers/               # Business logic controllers
│   ├── models/                    # Data models
│   ├── views/                     # Gradio-based UIs
│   ├── utils/                     # Shared utilities and helpers
│   ├── exceptions/                # Custom exception types
│   └── logs/                      # Logging infrastructure
│
├── flows/                         # Workflow implementations (bot-style automation)
├── integrations/                  # Third-party service integrations
├── ml_engine/                     # Machine learning system
├── postwizard_sdk/                # PostWizard REST SDK (internal client library)
├── wordpress/                     # WordPress integration layer
└── workflows/                     # Workflow orchestration and task composition
```


---

## 🧠 Machine Learning System (Implementation Notes)

The ML engine uses cached WordPress content as training data to build classifiers that predict
appropriate categories and tags.

- Tokenization and preprocessing via NLTK
- Multiple classifiers trained per feature type
- Serialized models stored locally and loaded at runtime
- Designed for retraining as category schemes evolve

---

## 🚀 Usage & Workflows

> ⚠️ **Note**
>
> The workflows in this repository are preserved for demonstration and experimentation purposes.
> Running them against live sites or third-party services requires careful review, appropriate
> credentials, and compliance with platform terms.

Implementation details, configuration UIs, and workflow entry points are preserved in the
repository for reference, but they are not organized as a step-by-step setup guide and may
require adaptation for modern environments.

---

## 🔒 Maintenance & Contributions

This repository is published as a **read-only reference implementation**.

- The project is not under active development
- Pull requests are unlikely to be reviewed or merged
- Issues may not receive responses

You are encouraged to **fork the repository** and adapt it to your own needs. This repository
itself should be considered **archived in spirit**, even if not formally archived on GitHub.

---

## 📝 License

This project is licensed under the **Mozilla Public License 2.0 (MPL-2.0)**.

MPL 2.0 was chosen to allow reuse of individual components while preserving attribution and
discouraging silent proprietary reuse of the complete system.

---

## ✉️ Contact

**Original Author:**  
**Yoham Gabriel**  
GitHub: [@Urbine](https://github.com/Urbine)

---

> **Disclaimer**
>
> This project is provided as-is for educational and reference purposes. The author makes no
> guarantees regarding correctness, security, or fitness for any particular use.
>
> Users are solely responsible for compliance with applicable laws, platform terms of service,
> and content regulations.

---

**Project Status:** Completed Internal Project — Open-Sourced Reference Implementation  
**Active Development:** None
