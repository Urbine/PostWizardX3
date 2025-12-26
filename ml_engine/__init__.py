# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

try:
    from ml_engine.classifiers import (
        classify_title,
        classify_description,
        classify_tags,
    )
except LookupError:
    import nltk

    nltk.download("stopwords")
    nltk.download("punkt_tab")

    from ml_engine.classifiers import (
        classify_title,
        classify_description,
        classify_tags,
    )

__all__ = ["classify_title", "classify_description", "classify_tags"]
