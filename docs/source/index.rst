.. webmaster-seo-tools documentation master file, created by
   sphinx-quickstart on Wed Nov  6 10:28:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

webmaster-seo-tools documentation
=================================

Welcome to the ``webmaster-seo-tools`` project documentation.

Here we will explore this project and understand where you should start.

Introduction
____________

``webmaster-seo-tools`` is a content management assistant that aims at standardising processes related to
Search Engine Optimization (SEO), media retrieval from internet sources, data classification, process automation and
content upload for adult websites built on top of WordPress.

``webmaster-seo-tools`` uses a powerful and resourceful API that serves as an abstraction layer that was implemented
using mostly the Python Standard Library, certain third-party libraries and local modules developed specially for this project and business needs
which motivated the solutions herein implemented. As an word of caution, the ethos of this project,
and I am pretty sure of others of the same kind, is creative and non-conventional at all.
I am convinced about the fact that creative ideation and "imagineering" is what make projects so enriching and stimulating.

Overview
________

``webmaster-seo-tools`` has five main packages and a sixth one still under development.
In order of development:

1. ``core`` has helper utilities, custom exceptions, configuration manager, and configuration files.

2. ``integrations`` is home to implementations that interact with public and confidential APIs that retrieve
   and manipulate information from and to external data sources.

3. ``tasks`` contains independent modules that automate tasks and prepare data to be used by other modules.
   In total, this module contains two web automation programs and two parsers that normalise information gathered
   with the first two. In addition to those, this package includes a module that cleans outdated files.

4. ``workflows`` boasts four job controllers that have the power of all the modules in the package.
   In here, three bots (job controllers, in theory) are in charge of content management and the fourth program
   coordinates all the tasks in the ``tasks`` package in a single workflow.

5. ``ml_engine`` is the brain behind content classification in the project, although part of it uses
   the powerful ``integrations.wordpress_api`` for tag matching, among other routines in that module.
   This package contains Machine Learning classifiers that can be trained to analyse the language and tags
   of video content so as to assign and/or suggest a suitable category.
   ``ml_engine`` trains nine models with algorithms like NaiveBayes, MaxEntropy and Multinomial NaiveBayes.

6. ``setup`` is still under development and aims at preparing the project for an eventual and not-yet-defined distribution release.






.. toctree::
   :maxdepth: 2
   :caption: Packages:

   core
   integrations
   tasks
   workflows
   ml_engine









