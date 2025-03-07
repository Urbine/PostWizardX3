*********************************
webmaster-seo-tools documentation
*********************************

Welcome to the ``webmaster-seo-tools`` for WM project documentation.

Here we will explore this project and understand where you should start.

Introduction
============

``webmaster-seo-tools`` is a content management assistant that aims at standardising processes related to
Search Engine Optimization (SEO), media retrieval from internet sources, data classification, process automation and
content upload for adult websites built on top of WordPress.

``webmaster-seo-tools`` uses a powerful and resourceful API that serves as an abstraction layer that was implemented
using mostly the Python Standard Library, certain third-party libraries and local modules developed specially for this project.
For the most part, business needs motivated the solutions herein implemented.

As an word of caution, the spirit of this project, and I am pretty sure of others of the same kind, is creative and non-conventional at all.
I am convinced about the fact that creative ideation and "imagineering" is what make projects so enriching and stimulating.

Overview
========

``webmaster-seo-tools`` has five main packages and a sixth one still under development.
In order of development:

1. ``core`` has helper utilities, custom exceptions, configuration manager, and configuration files.

2. ``integrations`` is home to implementations that interact with public and confidential APIs that retrieve
   and manipulate information from and to external data sources.

3. ``tasks`` contains independent modules that automate tasks and prepare data to be used by other modules.
   In total, this module contains two web automation programs and two parsers that normalise information gathered
   with the first two. In addition to those, this package includes a module that cleans outdated files.

4. ``workflows`` boasts four bots that have the power of all the modules in the package.
   In here, three of them are in charge of content management and the fourth bot
   coordinates all the tasks in the ``tasks`` package in a single workflow.

5. ``ml_engine`` is the brain behind content classification in the project, although part of it uses
   the powerful ``integrations.wordpress_api`` for tag matching, among other routines in that module.
   This package contains Machine Learning classifiers that can be trained to analyse the language and tags
   of video content so as to assign and/or suggest a suitable category.
   ``ml_engine`` trains nine models with algorithms like NaiveBayes, Maximum Entropy Modelling and Multinomial NaiveBayes.

6. ``test`` contains unit test classes for several functions that may undergo refactoring and improvement now or in the
   future; also contains tests for critical functions that need to enforce certain functionality.

7. ``setup`` is still under development and aims at preparing the project for an eventual and not-yet-defined distribution release.

Quick Start
===========

In order that you can start using this project, you need to keep an up-to-date copy of your posts.
That said, it is important to start by updating your credentials to access your WordPress sites.

1. Install the projects dependencies with the following command

   .. code:: console

      $ pip install -r requirements.txt

2. Generate your config files by running this command in your terminal:

   .. code:: console

      $ python3 -m setup.config_create

3. After generating your config files, you can add your app password to the ``client_info.ini`` file.

   .. tip::
      If you want to know more about application passwords refer to:
      `Application Passwords <https://wordpress.com/support/security/two-step-authentication/application-specific-passwords/>`_ on WordPress.com


4. Build your posts ``.json`` file with this command:

   .. code:: console

      $ python3 -m integrations.wordpress_api --posts --yoast

   .. attention::
      This command assumes that you have the Yoast SEO plugin installed in WordPress.
      You can leave this flag out if your site does not have this plugin.
      I suggest you using it since the Yoast elements do not contain common HTML entities that you may not want to keep.

5. Add your additional credentials in the configuration ``client_info.ini``.
   ``webmaster-seo-tools`` has additional service integrations you can choose from:

   a. MongerCash Affiliate program

   .. code:: console

      $ python3 -m workflows.update_mcash_chain --hint <partner_hint> --gecko --headless

   .. tip::
      ``partner_hint`` can be the first word of you partner offering as the bot can match your partner
      with a significant word.
      The ``--gecko`` flag will use the Firefox webdriver for the login and data retrieval automation.
      ``--headless``, in this case, means "run the automation in the background" or "headless webdriver."


   b. TubeCorporate Feeds (VJAV, Desi Tube)

      Defaults are: no more than 100 video entries sorted by popularity in the last 7 days.
      You can modify the values according to your needs:

      .. code:: console

         $ python3 -m integrations.tube_corp_feeds -days 7 -sort popularity -limit 100

   c. AdultNext API (Abjav)

      For AdultNext, the default day count is 30 days. However, you can experiment with any value that works for the task at hand.

      .. code:: console

         $ python3 -m integrations.adult_next_api -days 30 -sort popularity -limit 100

   d. X (formerly Twitter) API

      ``webmaster-seo-tools`` incorporates automatic and semi-automatic post creation on X.

      .. tip::
         You can configure X posting behaviour in the ``workflows_config.ini`` file.
         Credentials and API Secrets are stored in ``client_info.ini`` for the entire project.

   e. Telegram BotFather API

      Send messages to your site's channel or group with this command:

      .. code:: console

         $ python3 -m integrations.botfather_telegram --msg "your message"

      .. note::
         The Telegram BotFather integrations works just like the X API from a configuration standpoint.
         For example, you can tweak automatic posting and disable the functionality
         from the ``workflows_config.ini`` configuration. For token and chat ID, set it up in
         ``client_info.ini`` with all other secrets in the project.

      .. tip::
         If you just configured your bot via Telegram, you can use the ``--getme`` flag to
         get information about it and check some defaults. Try it!

         .. code:: console

            $ python3 -m integrations.botfather_telegram --getme

   d. FapHouse API

      Obtain a fresh adult database with dynamic SQL schema configuration.
      For an optimal experience, you can try this out:

      .. code:: console

         $ python3 -m integrations.fhouse_api --no-embed-dur

      This command will exclude the ``embed_dur`` column which is not
      relevant for processing, however, you can still include it if you so want it by
      removing the flag.

      .. tip::
         For more information about options supported by each integration,
         run the module with the ``--help`` flag:

         .. code:: console

            $ python3 -m integrations.fhouse_api --help



Get to Know the Bots
====================

1. ``content_select`` is in charge of reading the databases produced by tasks associated with the
   MongerCash Affiliate Program and uploading video information to WordPress.

   .. code:: console

      $ python3 -m workflows.content_select

2. ``gallery_select`` is another bot that deals with information from MongerCash.
   In this case, we are talking about image sets, also known as "Galleries."

   .. code:: console

      $ python3 -m workflows.gallery_select --gecko

   .. warning::
      All modules dealing with webdriver automation have the ``--gecko`` and ``--headless`` flags,
      however, there are cases where it is not recommended to use headless mode.
      **This is one of those cases.** The ``--gecko`` flag can be omitted altogether and default to
      the Chrome browser driver if you so want it.

      Take into consideration that ``gallery_select`` downloads files and Chrome does not usually wait
      until current downloads finish before closing running browser instances; fixes have been applied here to correct that behaviour.

      Headless mode does not show users why a certain iteration of the program failed and, due to the many factors, including but not limited to,
      internet connection speeds, the browser instance may require user collaboration to ensure the file has been
      downloaded and the former could then be closed either automatically or explicitly.
      For this reason, refrain from using ``--headless`` mode with ``workflows.gallery_select``.

      For more information about the ``--headless`` mode and its performance considerations,
      jump to `Should you go headless? <troubleshooting.html#should-you-go-headless>`_

      If you are experiencing issues with either mode, check out
      `Webdriver Issues <troubleshooting.html#webdriver-issues>`_

3. ``embed_assist`` interacts with other content APIs that rely on embed codes to display content
   on WordPress. It reads, processes, and uploads the information from the AdultNext and TubeCorporate feeds
   to your site. Just like ``content_select``, ``embed_assist`` is the perfect assistant for curating content and
   pushing what you like to WordPress.

   .. code:: console

      $ python3 -m workflows.embed_assist

4. ``update_mchash_chain`` controls the tasks developed in the ``tasks`` package
   and ensures the consistency of their responsibility.
   It is useful when MongerCash releases updates as this bot will update the databases and rebuild them.

   .. code:: console

      $ python3 -m workflows.update_mcash_chain --hint partner_hint --gecko --headless

   .. note::
      ``--headless`` mode is fully supported in ``workflows.update_mcash_chain`` and use of ``--gecko``
      is optional as in other programs.

What's next?
============

You have just gone through an overview of ``webmaster-seo-tools`` and its tools.
Head over to any of the package pages if you feel curious about this project.

.. tip::
   If you ever want to look at the code associated with any of the docstrings, you can do so by
   clicking the ``[source]`` link.