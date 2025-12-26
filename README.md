# 🧙‍♂️ PostWizardX3

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](./LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **An Open-Source Proof of Concept for Content Publishing Automation**
>
> PostWizardX3 is an open-source **reference implementation** exploring automation patterns for
> content ingestion, classification, and publishing workflows built around WordPress.
>
> The project originated as part of a larger internal system that has since been discontinued.
> Rather than letting the engineering work disappear, it has been open-sourced as a learning
> resource and architectural showcase.

---

## 🚦 Project Status

**Status:** Proof of Concept / Reference Implementation

This repository is provided strictly as a **technical proof of concept**.

- ✅ Demonstrates real-world automation and orchestration patterns
- ✅ Codebase is functional and internally consistent
- ⚠️ APIs and workflows may change without notice
- ❌ No production guarantees
- ❌ No committed roadmap or maintenance promise

The project is **not an actively developed product**. Users are encouraged to fork and adapt the
codebase for their own needs.

---

## 🎯 Intended Audience

This project is primarily intended for:

- Developers studying automation-heavy system design
- Engineers exploring WordPress REST–based publishing workflows
- Readers interested in applied ML within real-world content pipelines

It is **not** intended to be used as a production-ready or supported system.

---

## 📌 Project Overview

PostWizardX3 is a Python-based automation framework demonstrating how a complex content publishing
pipeline can be orchestrated around WordPress. While the original use case focused on
**affiliate content**, the architectural patterns are broadly
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
content publishing. The original product or service is no longer active, but the engineering
work remains valuable as:

- A **reference implementation** for similar automation systems
- A **learning resource** for complex workflow orchestration
- A **proof of concept** demonstrating architectural and integration patterns
- A **foundation** for experimentation or selective reuse

---

## TL;DR

- 🔬 Proof of concept, not a product
- 🧠 Demonstrates automation + ML-driven publishing
- 🧩 Modular, bot-based architecture
- 🧪 Best used as a reference or experimentation base
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
- Content provider feeds

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
> and content regulations, particularly when working with entertainment-oriented material.

---

**Project Status:** Completed Internal Project — Open-Sourced Reference Implementation  
**Active Development:** None
