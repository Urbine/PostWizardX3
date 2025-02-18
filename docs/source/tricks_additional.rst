==============================
Tricks and Additional Features
==============================

There are quick tricks that will make you productive with the tools described here.
Read on to get familiar with them.

Clipboard interaction
=====================

Modules in the ``workflows`` and ``integrations`` packages have implemented clipboard handling logic,
which means that important pieces of information are automatically copied and
cleared from it whenever you no longer need it.

.. tip::
   The clipboard is not enabled by default in certain operating systems.
   For example, you can press the ``❖`` (also called ``Windows`` or ``Super``) key + ``V`` in other
   to enable it in Microsoft Windows.

   In case you are using a GNU/Linux distribution, consult its manual or your desktop environment documentation in order
   to make use of that capability. For example, if you use a distribution with GNOME, you need to install a clipboard
   manager extension via the extension manager and set up a keyboard binding.

You can access these pieces of data in your clipboard in order that you can paste them in the corresponding fields while
creating posts or interacting with the CLI.

.. tip::

   Feel free to use and paste values that ``workflows`` and ``integrations`` copy for you.

   1. ``integrations.x_api``

      | While authorising your application, web automation can make sure you don't have to interact
        with the flow, however, if program identifies any issues, it will ask you to continue the process manually.
        In this case, the bot will copy the authorisation URL for you and it will be ready for you to paste it into
        a browser window.

   2. Bots in the ``workflows`` package (except ``update_mchash_chain``)

      During your interaction with the bots, you will notice occasions where user input is required to complete
      post creation.

      * **Slug customisation:** If you choose to provide a custom slug, the default slug will be copied for you to
        modify it accordingly.

      * **Missing WordPress taxonomies:** the bots will tell you whether a tag or any other supported taxonomy (e.g., Model)
        is missing and copies it to the clipboard for its later addition to the WordPress site. *This will be a one-time
        process for each term.*

      * **Post title and source URLs:** A post creation workflow will only be complete once certain pieces of information
        are added on WordPress; this is why the bot will copy these details for you in a comprehensive paste order.

      * **Custom social messages:** If you have been reading other parts of this documentation, you will see that
        ``workflows`` are equipped with two social integrations: X (formerly Twitter) and Telegram BotFather.
        Whenever you have to type in a message for one, the same message will be copied for you in case messages
        are identical.

.. caution::
   Do not try to copy pieces of information using ``CTRL`` + ``C`` as you will terminate the current program
   and generate a ``KeyboardInterrupt`` exception. If this happens, I handle this exception intentionally as a smooth termination
   of the program to be able to perform clean up operations. **Now, if you really want to quit
   the application, you can do it this way without any issues.**

Temporary Storage
=================

Adult content is sensitive and privacy regarding any activities related to it are to be taken seriously.
Modules across packages protect users' fingerprint by providing them with automatic and dynamic temporary storage for
every session.

.. note::
   ``workflows``, ``integrations`` and ``Tasks`` keep certain elements volatile and isolated within sessions.
   Every time a user starts a session, a unique temporary directory is created as a workspace for the
   bot during runtime.

   Temporary storage applies for the following:

   1. Downloaded files from the internet.

   2. Archive extraction.

   3. Thumbnail rename, handling and removal.

   4. Intermediate results from operations like data consolidation and parsing.


Image Conversion
================

Use of next-generation image formats are key to a fast site with quality and efficiency in mind.
Bots in the ``workflows`` package offer image conversion via ``ImageMagick`` system binaries.

.. tip::
   You can enable or disable this feature in the ``workflows_config.ini`` configuration file.

   Here is a part of that configuration file dealing with Image Conversion:

   .. code-block:: ini

      [general_config]
      pic_format = .webp
      imagick_enabled = False
      conversion_quality = 80
      fallback_pic_format = .jpg

   There exist some considerations before using this functionality:

   * Consider whether or not ImageMagick is enabled in configuration before using
     next-gen image formats in ``pic_format``.

   * Find the correct image quality value for lossy image conversion. A conversion quality
     value of ``80`` is reasonable and recommended for most sites.

   * Set up a fallback image format if ``ImageMagick`` is not enabled, not found or not
     installed in your system. This is usually the source format of thumbnails or
     images you usually download and plan to utilise on WordPress.

.. seealso::
   If you have any other issues related to configuration files or options, visit
   `Configuration Management <config_mgr.html#configuration-management>`_

.. seealso::
   If you want to know more about ``ImageMagick``, visit their `Wikipedia <https://en.wikipedia.org/wiki/ImageMagick>`_
   entry.

Social Posting Assistance
=========================

``content_select``, ``gallery_select`` and ``embed_assist`` feature a manual and automatic modes for interacting with
X and Telegram. In general, social posting makes use of a predefined template which contains a link to a published
post on WordPress plus a call-to-action. **For now, calls-to-action are predefined as well.**

.. tip::
   Enable or disable automatic social posting in the ``workflows_config.ini`` configuration file.
   If the ``auto`` mode is disabled, the bot will ask you to provide a message for each post you create.
   In case the messages are identical for both platforms, the bot will copy the first message so you don't
   have to type it in again, just paste it when prompted for the second time.

.. seealso::
   Look at the `content_select.x_post_creator <workflows.html#workflows.content_select.x_post_creator>`_ and
   `content_select.telegram_send_message <workflows.html#workflows.content_select.telegram_send_message>`_
   code and documentation if you want to understand more about the post creation mechanism I am referring to
   in this section.

Standard Input Manipulation
===========================

Input fields in the ``workflows`` package include the editing and history capabilities from the ``GNU Readline`` library.

.. note::
   **What does this mean for me as a user?**

   This component will allow you to move freely, forward and backwards, while editing text in any input
   field or prompt by ``workflows`` bots. In addtion to that, you have access to session history and keyboard
   bindings that will enhance your experience. For example, you can press ``↑`` or ``CTRL`` + ``P`` to go back to
   your previous input text/command.

.. seealso::
   If you want to know more about the keyboard motions of the ``GNU Readline`` library,
   take a look a simple introduction on `Wikipedia - GNU Readline <https://en.wikipedia.org/wiki/GNU_Readline>`_

