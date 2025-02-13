ml\_engine package
==================
At the heart of content classification efforts, resides a powerful fellow called ``ml_engine``.

Machine Learning probabilistic models are widely used for tasks, including but not limited to,
Natural Language Processing (NLP), Search Engine Optimisation (SEO), among other subject matters where
text classification relies on reinforcement of tagged data.

After some months of human classification of adult videos and tagging aided by ``integrations.wordpress_api``,
I secured a training set of 600 videos that reunited the characteristics of the classification scheme used on the site.
Out those many videos, around 80% were used to train 9 models and 20% were used to validate suggestions in the first days of development.

.. note::
   As of now, the ``ml_engine.model_train`` module uses 100% of data observations to ensure cummulative improvement,
   however, ML classification is still in the early stages of testing, so I do not recommend you rely on it entirely.

   **Instead, if you believe that categories do not match the video, description or tags, classify the video yourself
   to allow for an increase in model accuracy. Interestingly enough, the model can be pretty accurate with obvious observations,
   but focusing on granularity will help it become better with edge cases.**

.. tip::
   If you want to obtain further information regarding the Machine Learning models used in this package,
   jump to `ml_engine.model_train <ml_engine.html#module-ml_engine.model_train>`_

.. seealso::
   If you like to get into gory details, have a look at the following documentation:

   `Source code for nltk.classify.naivebayes <https://www.nltk.org/_modules/nltk/classify/naivebayes.html>`_

   `Source code for nltk.classify.maxent <https://www.nltk.org/_modules/nltk/classify/maxent.html>`_

   `MultinomialNB <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html>`_



Submodules
----------

ml\_engine.classifiers module
-----------------------------

.. automodule:: ml_engine.classifiers
   :members:
   :undoc-members:
   :show-inheritance:

ml\_engine.model\_train module
------------------------------

.. automodule:: ml_engine.model_train
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: ml_engine
   :members:
   :undoc-members:
   :show-inheritance:
