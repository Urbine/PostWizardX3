import re
from itertools import chain


from nltk import word_tokenize, NaiveBayesClassifier, SklearnClassifier
from nltk.classify import MaxentClassifier
from sklearn.naive_bayes import MultinomialNB

import nltk.corpus
import joblib
import time

# Local implementations
from core import helpers, WP_CLIENT_INFO
from integrations import wordpress_api


def clean_descriptions(desc_lst: list[str]):
    descriptions = desc_lst
    clean_desc = []
    for description in descriptions:
        # Descriptions has a <title> - <description> format.
        re_split_char = re.compile(r'[\W_+]')
        find_re = re.findall(re_split_char, description)
        try:
            clean = description.split(find_re[find_re.index('-')])[0].strip()
            clean_desc.append(clean)
        except ValueError:
            clean_desc.append(description)
        finally:
            continue
    return clean_desc


def clean_titles(titles: list[str]):
    clean_title = []
    for t in titles:
        # Descriptions has a <title> - <description> format.
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


def get_training_set(training_set: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """ Calculate and extract 80% of the training set for classifier training.
    :param training_set: ``list[tuple[str, str, str]]``
    :return: ``list[tuple[str, str, str]]``
    """
    return [training_set[indx_data]
            for indx_data in range(0, int(len(training_set) * 0.8))]


def get_testing_set(training_set: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """ Calculate and extract 20% of the training set for classifier testing.
        :param training_set: ``list[tuple[str, str, str]]``
        :return: ``list[tuple[str, str, str]]``
        """
    return [training_set[indx] for indx in range(int(len(training_set) * 0.8), len(training_set))]


def wp_get_training_data() -> tuple[list[tuple[str, str, str]], list[tuple[str, str]]]:
    import_wp_cache = helpers.load_json_ctx(WP_CLIENT_INFO.wp_posts_file)
    title = wordpress_api.get_post_titles_local(import_wp_cache, yoast=True)
    raw_descriptions = wordpress_api.get_post_descriptions(import_wp_cache, yoast=True)
    categories = wordpress_api.get_post_category(import_wp_cache)
    data_tag_categ = wordpress_api.map_wp_class_id_many(import_wp_cache, 'tag', 'category')

    return (list(zip(title, clean_descriptions(raw_descriptions), categories)),
            list(zip([','.join(list(st)) for st in data_tag_categ.values()], data_tag_categ.keys())))

# A more accurate way to train a classifier could be done with the help of
# tags. To be explored...
from typing import Tuple, List
# Start by creating our training set
all_training_data = wp_get_training_data()
title_desc_training_data = all_training_data[0]
training_data_tag_categ = all_training_data[1]

# Define stop words
stop_words_english = set(nltk.corpus.stopwords.words('english'))
stop_words_english.update(['.', ',', '"', "'", '?', '¿', '¡', '!', ':',
                           ';', '(', ')', '[', ']', '{', '}', '&amp;',
                           '&period', 'Pornhub&period;com&comma', 'Pornhub', '&', '#'])

# Obtain all the vocabulary
vocabulary_titles = set(chain(*[word_tokenize(t_data[0].lower()) for t_data in title_desc_training_data]))
vocabulary_descriptions = set(chain(*[word_tokenize(t_data[1].lower()) for t_data in title_desc_training_data]))
vocabulary_tags = list(chain(*[word_tokenize(t_data[0].lower()) for t_data in training_data_tag_categ]))


if __name__ == '__main__':
    # Measure execution time
    start_time = time.time()

    print("Training Machine Learning Classifier Models. Please wait...")

    word_list_titles = [({word: (word in word_tokenize(title.lower()))
                          for word in vocabulary_titles if word not in stop_words_english}, category)
                        for title, description, category in title_desc_training_data]

    word_list_descriptions = [({word: (word in word_tokenize(description.lower()))
                                for word in vocabulary_descriptions if word not in stop_words_english}, category)
                              for title, description, category in title_desc_training_data]

    word_list_tags = [({word: (word in word_tokenize(tags.lower()))
                                for word in vocabulary_tags if word not in stop_words_english}, category)
                              for tags, category in training_data_tag_categ]

    # Naive Bayes Classifier with titles
    NaiveBClassifier_titles = NaiveBayesClassifier.train(word_list_titles)

    # Naive Bayes Classifier with descriptions
    NaiveBClassifier_descriptions = NaiveBayesClassifier.train(word_list_descriptions)

    # Naive Bayes Classifier with tags
    NaiveBClassifier_tags = NaiveBayesClassifier.train(word_list_tags)

    # Maxent Classifier with hyperparameters
    maxent_cl_titles = MaxentClassifier.train(word_list_titles, trace=0, max_iter=50, min_lldelta=0.01)
    maxent_cl_descriptions = MaxentClassifier.train(word_list_descriptions, trace=0, max_iter=50, min_lldelta=0.01)
    maxent_cl_tags = MaxentClassifier.train(word_list_tags, trace=0, max_iter=50, min_lldelta=0.01)

    # Multinomial NB from Scikit-learn
    sklearn_classifier = SklearnClassifier(MultinomialNB())
    sk_class_titles = sklearn_classifier.train(word_list_titles)
    sk_class_descriptions = sklearn_classifier.train(word_list_descriptions)
    sk_class_tags = sklearn_classifier.train(word_list_tags)

    # NLTK NaiveBayes Classifier Model
    nbc_titles = './ml_models/NaiveBayesTitles.joblib.pkl'
    nbc_descriptions = './ml_models/NaiveBayesDescriptions.joblib.pkl'
    nbc_tags = './ml_models/NaiveBayesTags.joblib.pkl'
    save_nbc_titles = joblib.dump(NaiveBClassifier_titles, nbc_titles, compress=9)
    save_nbc_descriptions = joblib.dump(NaiveBClassifier_descriptions, nbc_descriptions, compress=9)
    save_nbc_tags = joblib.dump(NaiveBClassifier_tags, nbc_tags, compress=9)

    # NLTK Maxent Classifier
    maxent_titles = './ml_models/MaxentClassifierTitles.joblib.pkl'
    maxent_descriptions = './ml_models/MaxentClassifierDescriptions.joblib.pkl'
    maxent_tags = './ml_models/MaxentClassifierTags.joblib.pkl'
    save_maxent_titles = joblib.dump(maxent_cl_titles, maxent_titles, compress=9)
    save_maxent_descriptions = joblib.dump(maxent_cl_descriptions, maxent_descriptions, compress=9)
    save_maxent_tags = joblib.dump(maxent_cl_tags, maxent_tags, compress=9)

    # SciKit-Learn Classifier (Multinomial Naive Bayes)
    multinb_titles = './ml_models/MultiNBClassifierTitles.joblib.pkl'
    multinb_descriptions = './ml_models/MultiNBClassifierDescriptions.joblib.pkl'
    multinb_tags = './ml_models/MultiNBClassifierTags.joblib.pkl'
    save_multi_titles = joblib.dump(sk_class_titles, multinb_titles, compress=9)
    save_multi_descriptions = joblib.dump(sk_class_descriptions, multinb_descriptions, compress=9)
    save_multi_tags = joblib.dump(sk_class_tags, multinb_tags, compress=9)

    # End of execution time
    end_time = time.time()
    hours, minutes, seconds = helpers.get_duration(end_time - start_time)
    print(f"\nTraining took {int(hours)} hours, {int(minutes)} minutes and {int(seconds)} seconds.\n")
