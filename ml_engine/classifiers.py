"""
Classifier moduler

Load and export the most important functions that implement the three NaiveBayes models
selected for this task. The module is meant to export these functions to the main programs
in the ``workflows`` package to aid in the classification of features like title, description and categories.

In order that you can use this module, the machine learning models must be trained first with the
``ml_engine.model_train`` program.

It is important to note that the models in this project are in the initial phases of training and accuracy
will be improved as users make independent classification decisions that will impact the models' learning.
Feel to select whatever makes sense if the models are not accurate in their predictions.
Classification models used in this project use the Supervised Learning methodology.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from nltk.tokenize import word_tokenize
import joblib

# Local modules
from core import load_file_path
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
    return {
        NaiveBayes_titles.classify(prep_title),
        Maxent_titles.classify(prep_title),
        Multinomial_titles.classify(prep_title),
    }


def classify_description(description: str) -> set[str]:
    """Classify a post description based on its word content.
        First prepare the data, and then pass it to the three classifiers in order to get
        a result set.

    :param title: ``str`` description of the post to be classified
    :return: ``set[str]`` Classification result set
    """
    prep_description = {
        word: (word in word_tokenize(description.lower()))
        for word in vocabulary_descriptions
        if word not in stop_words_english
    }
    return {
        NaiveBayes_descriptions.classify(prep_description),
        Maxent_descriptions.classify(prep_description),
        Multinomial_descriptions.classify(prep_description),
    }


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
    return {
        NaiveBayes_tags.classify(prep_tags),
        Maxent_tags.classify(prep_tags),
        Multinomial_tags.classify(prep_tags),
    }
