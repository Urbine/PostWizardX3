from nltk import NaiveBayesClassifier, SklearnClassifier
from nltk.classify import MaxentClassifier
from nltk.tokenize import word_tokenize
from sklearn.naive_bayes import MultinomialNB
import joblib

# Local modules
from model_train import vocabulary_titles, vocabulary_descriptions, stop_words_english

# Load the trained models

# NLTK NaiveBayesClassifier
NaiveBayes_titles = joblib.load('./ml_models/NaiveBayesTitles.joblib.pkl')
NaiveBayes_descriptions = joblib.load('./ml_models/NaiveBayesDescriptions.joblib.pkl')

# NLTK Maxent Classifier
Maxent_titles = joblib.load('./ml_models/MaxentClassifierTitles.joblib.pkl')
Maxent_descriptions = joblib.load('./ml_models/MaxentClassifierDescriptions.joblib.pkl')

# SciKit-Learn Classifier (Multinomial Naive Bayes)
Multinomial_titles = joblib.load('./ml_models/MultiNBClassifierTitles.joblib.pkl')
Multinomial_descriptions = joblib.load('./ml_models/MultiNBClassifierDescriptions.joblib.pkl')


def classify_title(title: str):
    prep_title = {word: (word in word_tokenize(title.lower())) for word in vocabulary_titles
                  if word not in stop_words_english}
    return {str(NaiveBayes_titles.classify(prep_title)),
            str(Maxent_titles.classify(prep_title)),
            str(Multinomial_titles.classify(prep_title))}


def classify_description(description: str):
    prep_description = {word: (word in word_tokenize(description.lower())) for word in
                        vocabulary_descriptions if word not in stop_words_english}
    return {str(NaiveBayes_titles.classify(prep_description)),
            str(Maxent_titles.classify(prep_description)),
            str(Multinomial_titles.classify(prep_description))}



