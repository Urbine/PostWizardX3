# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Classifier Module

This module provides machine learning classification capabilities using three different NaiveBayes
implementation models: NLTK NaiveBayesClassifier, NLTK MaxentClassifier, and Scikit-learn's
Multinomial NaiveBayes. These classifiers are used to analyze and categorize content based on
titles, descriptions, and tags.

The module exports functions that are utilized by the main programs in the ``workflows`` package
to assist in content classification tasks. It provides a more intelligent approach to categorizing
content, which helps maintain consistency across the website.

Before using this module, the machine learning models must be trained with the
``ml_engine.model_train`` program using existing website data as the training set.

Note that these models are in their initial training phase, and their accuracy will
improve over time as users make independent classification decisions that feed back
into the models' learning processes. If model predictions seem inaccurate, feel free
to select categories that make sense for your content.

All classification models in this project utilize Supervised Learning methodology.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging

from nltk.tokenize import word_tokenize
import joblib

# Local modules
from core.utils.file_system import load_file_path
from ml_engine.model_train import (
    vocabulary_titles,
    vocabulary_descriptions,
    vocabulary_tags,
    stop_words_english,
)

ML_ENGINE_PKG = "ml_engine.ml_models"


def _load_model(name: str):
    try:
        return joblib.load(load_file_path(ML_ENGINE_PKG, name))
    except OSError:
        logging.warning(
            "Model %s not found - run `ml_engine.model_train` to generate it.", name
        )
        return None


# NLTK NaiveBayesClassifier
NaiveBayes_titles = _load_model("NaiveBayesTitles.joblib.pkl")
NaiveBayes_descriptions = _load_model("NaiveBayesDescriptions.joblib.pkl")
NaiveBayes_tags = _load_model("NaiveBayesTags.joblib.pkl")

# NLTK Maxent Classifier
Maxent_titles = _load_model("MaxentClassifierTitles.joblib.pkl")
Maxent_descriptions = _load_model("MaxentClassifierDescriptions.joblib.pkl")
Maxent_tags = _load_model("MaxentClassifierTags.joblib.pkl")

# SciKit-Learn Classifier (Multinomial Naive Bayes)
Multinomial_titles = _load_model("MultiNBClassifierTitles.joblib.pkl")
Multinomial_descriptions = _load_model("MultiNBClassifierDescriptions.joblib.pkl")
Multinomial_tags = _load_model("MultiNBClassifierTags.joblib.pkl")


def categs_to_str(categs: set[str]):
    """
    Help to enforce ``str`` output when certain classifiers return instances of ``np.str_``

    :param categs: ``set[str]`` | resultset from the classifier process
    :return: ``set[str]``       | new resultset from the classifier process ensuring str typing.
    """
    categ_set = map(lambda categ: str(categ), categs)
    return set(categ_set)


def _classify(models: tuple, prep_data: dict[str, bool]) -> set[str]:
    """Run ``prep_data`` through every available model in ``models``.

    Models that could not be loaded (missing training artifacts) are skipped.
    Raises ``RuntimeError`` when no model is available to classify with.
    """
    available_models = [model for model in models if model is not None]
    if not available_models:
        raise RuntimeError(
            "No classification models available - run `ml_engine.model_train` to generate them."
        )
    results = {model.classify(prep_data) for model in available_models}
    return categs_to_str(results)


def classify_title(title: str) -> set[str]:
    """Classify a post title based on its word content.
    First prepare the data, and then pass it to the three classifiers in order to get
    a result set.

    :param title: ``str`` title of the post to be classified
    :return: ``set[str]`` Classification result set
    """
    prep_title = {
        word: (word in word_tokenize(title.lower()))
        for word in vocabulary_titles
        if word not in stop_words_english
    }
    return _classify(
        (NaiveBayes_titles, Maxent_titles, Multinomial_titles), prep_title
    )


def classify_description(description: str) -> set[str]:
    """Classify a post description based on its word content.
        First prepare the data, and then pass it to the three classifiers in order to get
        a result set.

    :param description: ``str`` description of the post to be classified
    :return: ``set[str]`` Classification result set
    """
    prep_description = {
        word: (word in word_tokenize(description.lower()))
        for word in vocabulary_descriptions
        if word not in stop_words_english
    }
    return _classify(
        (NaiveBayes_descriptions, Maxent_descriptions, Multinomial_descriptions),
        prep_description,
    )


def classify_tags(tag_str: str):
    """Classify post tags based on its independent words and occurrences in the entire site.
    The classifiers will locate a category where similar tag density was used in the site, thus,
    enhancing the coherence and integration of content with a certain category.
    Note that `Tags` are passed as a single comma-separated string.
    First prepare the data, and then pass it to the three classifiers in order to get
    a result set.

    :param title: ``str`` description of the post to be classified
    :return: ``set[str]`` Classification result set
    """
    prep_tags = {
        word: (word in word_tokenize(tag_str.lower()))
        for word in vocabulary_tags
        if word not in stop_words_english
    }
    return _classify(
        (NaiveBayes_tags, Maxent_tags, Multinomial_tags), prep_tags
    )
