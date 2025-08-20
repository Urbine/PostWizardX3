"""
Machine Learning Model Training Module

This module trains a set of machine learning models to classify WordPress content based on
cached posts data. It generates three types of classifiers, each trained on different content features:

1. NLTK NaiveBayesClassifier - For statistical classification using Bayes' theorem
2. NLTK MaxentClassifier - Maximum Entropy modeling for distribution-based classification
3. NLTK SklearnClassifier (MultinomialNB) - SciKit-learn integration with NLTK feature formatting

Each classifier type is trained on three different content features:
- Post titles
- Post descriptions
- Post tags

The resulting nine models are saved as compressed joblib files for later use in content
classification workflows. These models help predict appropriate content categories,
streamlining the publishing process and helping less experienced team members.

Running this module directly will:
1. Load cached WordPress posts data
2. Process and clean the text features
3. Create feature sets for each content type
4. Train all nine classifier models
5. Save the models to the ml_engine.ml_models package/directory.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import re
import time
from itertools import chain

# Machine Learning/NLP related
from nltk import word_tokenize, NaiveBayesClassifier, SklearnClassifier
from nltk.classify import MaxentClassifier
from sklearn.naive_bayes import MultinomialNB
import nltk.corpus
import joblib

# Local module implementations
from core.config.config_factories import general_config_factory
from core.models.secret_model import SecretType
from core.models.file_system import ApplicationPath
from core.controllers.secrets_controller import SecretHandler
from core.utils.helpers import get_duration
from core.utils.file_system import load_file_path
from wordpress.wordpress_api import WordPress
from wordpress.models.taxonomies import WPTaxonomyMarker


WP_AUTH = SecretHandler().get_secret(SecretType.WP_APP_PASSWORD)[0]
WP_SITE_INSTANCE = WordPress(
    general_config_factory().fq_domain_name,
    WP_AUTH.user,
    WP_AUTH.app_password,
    ApplicationPath.WP_POSTS_CACHE.value,
)


def clean_descriptions(desc_lst: list[str]):
    """Cleans a list of strings by extracting and returning the substring before a
    specified delimiter ('-') when present.

    :param desc_lst: ``list[str]`` A list of descriptions where each string follows
                        a '<title> - <description>' pattern.
    :return: ``list[str]`` A list of cleaned descriptions where the substring prior to the
                delimiter has been extracted, or the original string if the delimiter
                is not found.
    """
    descriptions = desc_lst
    clean_desc = []
    for description in descriptions:
        # Descriptions has a <title> - <description> format.
        re_split_char = re.compile(r"[^a-z]+", re.IGNORECASE)
        find_re = re.findall(re_split_char, description)
        try:
            clean = description.split(find_re[find_re.index("-")])[0].strip()
            clean_desc.append(clean)
        except ValueError:
            clean_desc.append(description)
    return clean_desc


def clean_titles(titles: list[str]):
    """Cleans a list of strings by extracting and returning titles before any dash
    delimiter when present.

    :param titles: ``list[str]`` A list of titles that may contain dash delimiters
    :return: ``list[str]`` A list of cleaned titles where content after dash delimiters
                has been removed, or the original string if no delimiter is found.
    """
    clean_title = []
    for t in titles:
        dash_out = t.split("-")
        if len(dash_out) >= 2:
            # Sometimes, I could hit a <title-something> - <description>
            # I also want to make sure not to get the call to action after the
            # period.
            if len(dash_out) == 3:
                clean_title.append("-".join(dash_out[0:1][0].strip()))
            else:
                clean_title.append(dash_out[0].strip())
        else:
            clean_title.append(t.split("-")[0].strip())
    return clean_title


def get_training_set(
    training_set: list[tuple[str, str, str]],
) -> list[tuple[str, str, str]]:
    """Calculate and extract 80% of the training set for classifier training.
    :param training_set: ``list[tuple[str, str, str]]``
    :return: ``list[tuple[str, str, str]]``
    """
    return [
        training_set[indx_data] for indx_data in range(0, int(len(training_set) * 0.8))
    ]


def get_testing_set(
    training_set: list[tuple[str, str, str]],
) -> list[tuple[str, str, str]]:
    """Calculate and extract 20% of the training set for classifier testing.
    :param training_set: ``list[tuple[str, str, str]]``
    :return: ``list[tuple[str, str, str]]``
    """
    return [
        training_set[indx]
        for indx in range(int(len(training_set) * 0.8), len(training_set))
    ]


def wp_get_training_data(
    wordpress_site: WordPress,
) -> tuple[list[tuple[str, str, str]], list[tuple[str, str]]]:
    """Combine the available data for models' training.

    :param wordpress_site: ``WordPress`` -> WordPress class instance
    :return: ``tuple[list[tuple[str, str, str]], list[tuple[str, str]]]``
    First element contains the structure ``(title, description, category)``
    Second element contains the structure ``(tags_str, category)``
    """
    title = wordpress_site.get_post_titles_local(yoast_support=True)
    raw_descriptions = wordpress_site.get_post_descriptions(yoast_support=True)
    categories = wordpress_site.get_post_category()
    data_tag_categ = wordpress_site.map_wp_class_id_many(
        WPTaxonomyMarker.TAG, WPTaxonomyMarker.CATEGORY
    )

    return (
        list(zip(title, clean_descriptions(raw_descriptions), categories)),
        list(
            zip(
                [",".join(list(st)) for st in data_tag_categ.values()],
                data_tag_categ.keys(),
            )
        ),
    )


# Start by creating our training set
all_training_data = wp_get_training_data(WP_SITE_INSTANCE)

# Index 0 contains the (title, description and category) data
title_desc_training_data = all_training_data[0]

# Index 1 contains the (tags, category) data
training_data_tag_categ = all_training_data[1]

# Define stop words to leave out irrelevant data.
stop_words_english = set(nltk.corpus.stopwords.words("english"))
stop_words_english.update(
    [
        ".",
        ",",
        '"',
        "'",
        "?",
        "¿",
        "¡",
        "!",
        ":",
        ";",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        "&amp;",
        "&period",
        "Pornhub&period;com&comma",
        "Pornhub",
        "&",
        "#",
    ]
)

# Obtain all the vocabulary for preliminary preparation.
vocabulary_titles = set(
    chain(*[word_tokenize(t_data[0].lower()) for t_data in title_desc_training_data])
)
vocabulary_descriptions = set(
    chain(*[word_tokenize(t_data[1].lower()) for t_data in title_desc_training_data])
)
vocabulary_tags = list(
    chain(*[word_tokenize(t_data[0].lower()) for t_data in training_data_tag_categ])
)

if __name__ == "__main__":
    # Execution time - Start
    start_time = time.time()

    print("Training Machine Learning Classifier Models. Please wait...")

    word_list_titles = [
        (
            {
                word: (word in word_tokenize(title.lower()))
                for word in vocabulary_titles
                if word not in stop_words_english
            },
            category,
        )
        for title, description, category in title_desc_training_data
    ]

    word_list_descriptions = [
        (
            {
                word: (word in word_tokenize(description.lower()))
                for word in vocabulary_descriptions
                if word not in stop_words_english
            },
            category,
        )
        for title, description, category in title_desc_training_data
    ]

    word_list_tags = [
        (
            {
                word: (word in word_tokenize(tags.lower()))
                for word in vocabulary_tags
                if word not in stop_words_english
            },
            category,
        )
        for tags, category in training_data_tag_categ
    ]

    # Naive Bayes Classifier with titles
    NaiveBClassifier_titles = NaiveBayesClassifier.train(word_list_titles)

    # Naive Bayes Classifier with descriptions
    NaiveBClassifier_descriptions = NaiveBayesClassifier.train(word_list_descriptions)

    # Naive Bayes Classifier with tags
    NaiveBClassifier_tags = NaiveBayesClassifier.train(word_list_tags)

    # Maxent Classifier with hyperparameters
    maxent_cl_titles = MaxentClassifier.train(
        word_list_titles, trace=1, max_iter=50, min_lldelta=0.01
    )
    maxent_cl_descriptions = MaxentClassifier.train(
        word_list_descriptions, trace=1, max_iter=50, min_lldelta=0.01
    )
    maxent_cl_tags = MaxentClassifier.train(
        word_list_tags, trace=1, max_iter=50, min_lldelta=0.01
    )

    # Multinomial NaiveBayes from Scikit-learn
    sklearn_classifier = SklearnClassifier(MultinomialNB())
    sk_class_titles = sklearn_classifier.train(word_list_titles)
    sk_class_descriptions = sklearn_classifier.train(word_list_descriptions)
    sk_class_tags = sklearn_classifier.train(word_list_tags)

    # NLTK NaiveBayes Classifier Model
    nbc_titles = load_file_path(
        ApplicationPath.ML_ENGINE_PKG.value, "NaiveBayesTitles.joblib.pkl"
    )

    nbc_descriptions = load_file_path(
        ApplicationPath.ML_ENGINE_PKG.value, "NaiveBayesDescriptions.joblib.pkl"
    )

    nbc_tags = load_file_path(
        ApplicationPath.ML_ENGINE_PKG.value, "NaiveBayesTags.joblib.pkl"
    )
    save_nbc_titles = joblib.dump(NaiveBClassifier_titles, nbc_titles, compress=9)
    save_nbc_descriptions = joblib.dump(
        NaiveBClassifier_descriptions, nbc_descriptions, compress=9
    )
    save_nbc_tags = joblib.dump(NaiveBClassifier_tags, nbc_tags, compress=9)

    # NLTK Maxent Classifier
    maxent_titles = load_file_path(
        ApplicationPath.ML_ENGINE_PKG.value, "MaxentClassifierTitles.joblib.pkl"
    )

    maxent_descriptions = load_file_path(
        ApplicationPath.ML_ENGINE_PKG.value, "MaxentClassifierDescriptions.joblib.pkl"
    )

    maxent_tags = load_file_path(
        ApplicationPath.ML_ENGINE_PKG.value, "MaxentClassifierTags.joblib.pkl"
    )

    save_maxent_titles = joblib.dump(maxent_cl_titles, maxent_titles, compress=9)
    save_maxent_descriptions = joblib.dump(
        maxent_cl_descriptions, maxent_descriptions, compress=9
    )
    save_maxent_tags = joblib.dump(maxent_cl_tags, maxent_tags, compress=9)

    # SciKit-Learn Classifier (Multinomial Naive Bayes)
    multinb_titles = load_file_path(
        ApplicationPath.ML_ENGINE_PKG.value, "MultiNBClassifierTitles.joblib.pkl"
    )

    multinb_descriptions = load_file_path(
        ApplicationPath.ML_ENGINE_PKG.value, "MultiNBClassifierDescriptions.joblib.pkl"
    )

    multinb_tags = load_file_path(
        ApplicationPath.ML_ENGINE_PKG.value, "MultiNBClassifierTags.joblib.pkl"
    )
    save_multi_titles = joblib.dump(sk_class_titles, multinb_titles, compress=9)
    save_multi_descriptions = joblib.dump(
        sk_class_descriptions, multinb_descriptions, compress=9
    )
    save_multi_tags = joblib.dump(sk_class_tags, multinb_tags, compress=9)

    end_time = time.time()
    hours, minutes, seconds = get_duration(end_time - start_time)
    print(
        f"\nTraining took {int(hours)} hours, {int(minutes)} minutes and {int(seconds)} seconds.\n"
    )
