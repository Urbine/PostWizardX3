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

# NLTK NaiveBayesClassifier
NaiveBayes_titles = joblib.load(
    load_file_path(ML_ENGINE_PKG, "NaiveBayesTitles.joblib.pkl")
)

NaiveBayes_descriptions = joblib.load(
    load_file_path(ML_ENGINE_PKG, "NaiveBayesDescriptions.joblib.pkl")
)

NaiveBayes_tags = joblib.load(
    load_file_path(ML_ENGINE_PKG, "NaiveBayesTags.joblib.pkl")
)

# NLTK Maxent Classifier
Maxent_titles = joblib.load(
    load_file_path(ML_ENGINE_PKG, "MaxentClassifierTitles.joblib.pkl")
)

Maxent_descriptions = joblib.load(
    load_file_path(ML_ENGINE_PKG, "MaxentClassifierDescriptions.joblib.pkl")
)

Maxent_tags = joblib.load(
    load_file_path(ML_ENGINE_PKG, "MaxentClassifierTags.joblib.pkl")
)

# SciKit-Learn Classifier (Multinomial Naive Bayes)
Multinomial_titles = joblib.load(
    load_file_path(ML_ENGINE_PKG, "MultiNBClassifierTitles.joblib.pkl")
)

Multinomial_descriptions = joblib.load(
    load_file_path(ML_ENGINE_PKG, "MultiNBClassifierDescriptions.joblib.pkl")
)

Multinomial_tags = joblib.load(
    load_file_path(ML_ENGINE_PKG, "MultiNBClassifierTags.joblib.pkl")
)


def categs_to_str(categs: set[str]):
    """
    Help to enforce ``str`` output when certain classifiers return instances of ``np.str_``

    :param categs: ``set[str]`` | resultset from the classifier process
    :return: ``set[str]``       | new resultset from the classifier process ensuring str typing.
    """
    categ_set = map(lambda categ: str(categ), categs)
    return set(categ_set)


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
    results = {
        NaiveBayes_titles.classify(prep_title),
        Maxent_titles.classify(prep_title),
        Multinomial_titles.classify(prep_title),
    }
    return categs_to_str(results)


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
    results = {
        NaiveBayes_descriptions.classify(prep_description),
        Maxent_descriptions.classify(prep_description),
        Multinomial_descriptions.classify(prep_description),
    }
    return categs_to_str(results)


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
    results = {
        NaiveBayes_tags.classify(prep_tags),
        Maxent_tags.classify(prep_tags),
        Multinomial_tags.classify(prep_tags),
    }
    return categs_to_str(results)
