from itertools import chain
from nltk import NaiveBayesClassifier, SklearnClassifier
from nltk.classify import MaxentClassifier
from nltk import word_tokenize
from sklearn.naive_bayes import MultinomialNB
import nltk.corpus
import joblib

# Local implementations
from core import helpers, WP_CLIENT_INFO
from integrations import wordpress_api


def clean_descriptions(desc_lst: list[str]):
    descriptions = desc_lst
    clean_desc = []
    for description in descriptions:
        # Descriptions has a <title> - <description> format.
        dash_out = description.split("-")
        if len(dash_out) >= 2:
            # Sometimes, I could hit a <title-something> - <description>
            # I also want to make sure not to get the call to action after the
            # period.
            if len(dash_out) == 3:
                clean_desc.append(dash_out[2:][0].strip().split(".")[0])
            else:
                clean_desc.append(dash_out[1].split(".")[0])
        else:
            clean_desc.append(description.split(".")[0].strip())
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


def wp_get_training_data() -> list[tuple[str, str, str]]:
    import_wp_cache = helpers.load_json_ctx(WP_CLIENT_INFO.wp_posts_file)
    title = wordpress_api.get_post_titles_local(import_wp_cache, yoast=True)
    raw_descriptions = wordpress_api.get_post_descriptions(import_wp_cache, yoast=True)
    categories = wordpress_api.get_post_category(import_wp_cache)
    return list(zip(title, clean_descriptions(raw_descriptions), categories))


# A more accurate way to train a classifier could be done with the help of
# tags. To be explored...

# Start by creating our training set
all_training_data = wp_get_training_data()

# Define stop words
stop_words_english = set(nltk.corpus.stopwords.words('english'))
stop_words_english.update(['.', ',', '"', "'", '?', '¿', '¡', '!', ':',
                           ';', '(', ')', '[', ']', '{', '}', '&amp;',
                           '&period', 'Pornhub&period;com&comma', 'Pornhub', '&', '#'])

# Obtain all the vocabulary
vocabulary_titles = set(chain(*[word_tokenize(t_data[0].lower()) for t_data in all_training_data]))
vocabulary_descriptions = set(chain(*[word_tokenize(t_data[1].lower()) for t_data in all_training_data]))

if __name__ == '__main__':
    word_list_titles = [({word: (word in word_tokenize(title.lower()))
                          for word in vocabulary_titles if word not in stop_words_english}, category)
                        for title, description, category in all_training_data]

    word_list_descriptions = [({word: (word in word_tokenize(description.lower()))
                                for word in vocabulary_descriptions if word not in stop_words_english}, category)
                              for title, description, category in all_training_data]

    # Naive Bayes Classifier with titles
    NaiveBClassifier_titles = NaiveBayesClassifier.train(word_list_titles)

    # Naive Bayes Classifier_descriptions
    NaiveBClassifier_descriptions = NaiveBayesClassifier.train(word_list_descriptions)

    # Maxent Classifier with hyperparameters
    max_cl_titles = MaxentClassifier.train(word_list_titles, trace=0, max_iter=50, min_lldelta=0.01)
    max_cl_descriptions = MaxentClassifier.train(word_list_descriptions, trace=0, max_iter=50, min_lldelta=0.01)

    # Multinomial NB from Scikit-learn
    sklearn_classifier = SklearnClassifier(MultinomialNB())
    sklearn_classifier.train(word_list_titles)
    sklearn_classifier.train(word_list_descriptions)

    # NLTK NaiveBayes Classifier Model
    nbc_titles = './ml_models/NaiveBayesTitles.joblib.pkl'
    nbc_descriptions = './ml_models/NaiveBayesDescriptions.joblib.pkl'
    save_nbc_titles = joblib.dump(NaiveBClassifier_titles, nbc_titles, compress=9)
    save_nbc_descriptions = joblib.dump(NaiveBClassifier_descriptions, nbc_descriptions, compress=9)

    # NLTK Maxent Classifier
    max_titles = './ml_models/MaxentClassifierTitles.joblib.pkl'
    max_descriptions = './ml_models/MaxentClassifierDescriptions.joblib.pkl'
    save_max_titles = joblib.dump(max_cl_titles, max_titles, compress=9)
    save_max_descriptions = joblib.dump(max_cl_descriptions, max_descriptions, compress=9)

    # SciKit-Learn Classifier (Multinomial Naive Bayes)
    multinb_titles = './ml_models/MultiNBClassifierTitles.joblib.pkl'
    multinb_descriptions = './ml_models/MultiNBClassifierDescriptions.joblib.pkl'
    save_multi_titles = joblib.dump(sklearn_classifier, multinb_titles, compress=9)
    save_multi_descriptions = joblib.dump(sklearn_classifier, multinb_descriptions, compress=9)
