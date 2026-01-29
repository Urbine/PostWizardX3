# 🧙‍♂️ PostWizardX3

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](./LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
![Status: Archived](https://img.shields.io/badge/status-archived-lightgrey.svg)

PostWizardX3 is a comprehensive content management system built for WordPress, with a focus on video entertainment websites. It provides an end-to-end automation pipeline for **entertainment-oriented, age-restricted affiliate content**, while demonstrating architectural patterns broadly applicable to automation-heavy publishing systems.

PostWizardX3 was designed to operate alongside [PostWizardREST](https://github.com/Urbine/PostWizardREST) as a client-side automation and machine-learning layer, delegating high-throughput persistence, validation, and security-sensitive operations to a dedicated backend service.

---

> **Historical context**
>
> PostWizardX3 was developed as an internal automation and content management system and is no longer actively maintained. The documentation and code are preserved for architectural reference and educational purposes, reflecting the system’s design and capabilities at the time of active development.

---

## 🚦 Project Status

**Status:** Archived / Not Maintained

This repository is preserved for reference and educational purposes only.

* ✅ Fully functional codebase with multiple integrated components
* ⚠️ No longer actively maintained or supported
* ⚠️ Dependencies may be outdated
* ❌ No security updates or bug fixes
* ❌ Not recommended for production use without significant updates


## 🎯 High-Level Capabilities

* **Content Management**

  * Automated WordPress post creation and management
  * Video content processing and classification
  * Thumbnail and asset handling

* **Machine Learning**

  * Content classification using scikit-learn
  * Natural language processing for content analysis
  * Model training and evaluation utilities

* **Workflow Automation**

  * Batch-oriented content processing
  * Automated artifact selection
  * Content synchronization workflows


## 🛠️ Technical Stack

* **Language:** Python 3.11+
* **ML Stack:** scikit-learn, NLTK, NumPy, SciPy
* **Web:** aiohttp, requests, BeautifulSoup4
* **WordPress:** REST API integration
* **Build & Tools:** Ruff, uv


## 📌 Project Overview

This project demonstrates a modular, automation-first approach to managing WordPress-based publishing pipelines.

### What This Project Demonstrates

* End-to-end content automation workflows for WordPress sites
* Modular, bot-driven architectures for distinct content types
* Practical application of NLP-based classification in publishing pipelines
* Multi-source content ingestion and normalization
* Integration patterns for third-party APIs
* Configuration-driven extensibility with minimal hardcoding

### Original Context

PostWizardX3 was originally built as an internal tool for managing high-volume, automated content publishing. While the original product and service are no longer active, the engineering work remains valuable as:

* A **reference implementation** for automation-heavy publishing systems
* A **learning resource** for complex workflow orchestration
* A **production-grade example** of architectural and integration patterns
* A **foundation** for experimentation or adaptation

## TL;DR

* 🏛️ Archived project, not actively maintained
* 🧠 Complete automation and ML-driven publishing system
* 🧩 Modular, bot-based architecture
* ⚠️ Requires updates for production use
* ❌ No guaranteed maintenance or support


## 🌟 Detailed Features

### 🤖 Machine Learning Classification

* Ensemble-based text classification using:

  * NLTK Naive Bayes
  * NLTK Maximum Entropy
  * Scikit-learn Multinomial Naive Bayes (TF-IDF)
* Category, tag, and description-based predictions
* Designed for large-scale, semi-automated publishing workflows
* Supports retraining using corrected classifications

### 📝 Content Management

* WordPress REST API integration with authentication handling
* Local caching for efficient synchronization
* Automated category, tag, and media management
* SQLite-based repositories for ingestion and staging

### 🎬 Specialized Content Workflows

The system includes multiple **bot-style workflows**, each implementing a shared interface:

* Video content automation
* Photo gallery automation
* Embed-based publishing
* Database synchronization and updates

These workflows are intended to demonstrate architectural and orchestration patterns rather than serve as polished end-user tools.

### 🌐 External Integrations

* WordPress REST API
* Social platforms (X/Twitter, Telegram)
* Search APIs (multiple providers)
* Video entertainment provider feeds

### 🔧 Configuration & Administration

* Interactive Gradio-based configuration interfaces
* File-based configuration and secrets management
* Support for multiple authentication and API key types

## 🏗️ Architecture Overview

### Core Architectural Patterns

* **Factory Pattern** — configuration object creation
* **MVC-inspired separation** — models, controllers, and Gradio-based views
* **Strategy Pattern** — interchangeable automation workflows
* **Adapter Pattern** — unified interfaces over third-party APIs
* **Builder Pattern** — request and payload construction

### Project Structure

```
PostWizardX3/
├── core/                          # Core framework and utilities
│   ├── config/                    # Configuration management
│   ├── controllers/               # Business logic controllers
│   ├── models/                    # Data models
│   ├── views/                     # Gradio-based UIs
│   ├── utils/                     # Shared utilities
│   ├── exceptions/                # Custom exception types
│   └── logs/                      # Logging infrastructure
│
├── flows/                         # Bot-style workflow implementations
├── integrations/                  # Third-party service integrations
├── ml_engine/                     # Machine learning system
├── postwizard_sdk/                # Internal PostWizardREST integration SDK
├── wordpress/                     # WordPress integration layer
└── workflows/                     # Workflow orchestration and composition
```

## 🧠 Machine Learning System (Implementation Notes)

The ML engine uses cached WordPress content as training data to build classifiers that predict appropriate categories and tags.

* Tokenization and preprocessing via NLTK
* Multiple classifiers trained per feature type
* Serialized models stored locally and loaded at runtime
* Designed for retraining as category schemes evolve

## 🔒 Maintenance & Contributions

This repository is published as a **read-only reference implementation**.

* No active development
* Pull requests are unlikely to be reviewed or merged
* Issues may not receive responses

## 📝 License

This project is licensed under the **Mozilla Public License 2.0 (MPL-2.0)**.

> **Disclaimer**
>
> This project is provided as-is for educational and reference purposes. The author makes no guarantees regarding correctness, security, or fitness for any particular use.
>
> Users are solely responsible for compliance with applicable laws, terms of service, and content regulations.

---

**Project Status:** Completed Internal Project — Open-Sourced Reference Implementation
**Active Development:** None