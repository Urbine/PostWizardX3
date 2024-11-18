from nltk.classify import NaiveBayesClassifier, SklearnClassifier, MaxentClassifier
from nltk.tokenize import word_tokenize
from sklearn.naive_bayes import MultinomialNB
import joblib

# Local modules
from core import load_file_path
from ml_engine.model_train import (vocabulary_titles,
                                   vocabulary_descriptions,
                                   vocabulary_tags,
                                   stop_words_english)

# Load the trained models

# NLTK NaiveBayesClassifier
NaiveBayes_titles = joblib.load(load_file_path('ml_engine.ml_models',
                                               'NaiveBayesTitles.joblib.pkl'))

NaiveBayes_descriptions = joblib.load(load_file_path('ml_engine.ml_models',
                                                     'NaiveBayesDescriptions.joblib.pkl'))

NaiveBayes_tags = joblib.load(load_file_path('ml_engine.ml_models',
                                             'NaiveBayesTags.joblib.pkl'))

# NLTK Maxent Classifier
Maxent_titles = joblib.load(load_file_path('ml_engine.ml_models',
                                           'MaxentClassifierTitles.joblib.pkl'))

Maxent_descriptions = joblib.load(load_file_path('ml_engine.ml_models',
                                                 'MaxentClassifierDescriptions.joblib.pkl'))

Maxent_tags = joblib.load(load_file_path('ml_engine.ml_models',
                                                 'MaxentClassifierTags.joblib.pkl'))

# SciKit-Learn Classifier (Multinomial Naive Bayes)
Multinomial_titles = joblib.load(load_file_path('ml_engine.ml_models',
                                                'MultiNBClassifierTitles.joblib.pkl'))

Multinomial_descriptions = joblib.load(load_file_path('ml_engine.ml_models',
                                                      'MultiNBClassifierDescriptions.joblib.pkl'))

Multinomial_tags = joblib.load(load_file_path('ml_engine.ml_models',
                                              'MultiNBClassifierTags.joblib.pkl'))


def classify_title(title: str):
    prep_title = {word: (word in word_tokenize(title.lower())) for word in vocabulary_titles
                  if word not in stop_words_english}
    return {NaiveBayes_titles.classify(prep_title),
            Maxent_titles.classify(prep_title),
            Multinomial_titles.classify(prep_title)}


def classify_description(description: str):
    prep_description = {word: (word in word_tokenize(description.lower())) for word in
                        vocabulary_descriptions if word not in stop_words_english}
    return {NaiveBayes_descriptions.classify(prep_description),
            Maxent_descriptions.classify(prep_description),
            Multinomial_descriptions.classify(prep_description)}


def classify_tags(tag_str: str):
    prep_tags = {word: (word in word_tokenize(tag_str.lower())) for word in
                 vocabulary_tags if word not in stop_words_english}
    return {NaiveBayes_tags.classify(prep_tags),
            Maxent_tags.classify(prep_tags),
            Multinomial_tags.classify(prep_tags)}
