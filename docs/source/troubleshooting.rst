Troubleshooting
===============

Software packages always come with little quirks and this is no exception to the rule.
In this section, I will take you through a tour to the depths of known issues, optimisations and
what to do if the modules are not working as expected.

About Exceptions
________________

During development, I have identified several issues that programs in this project encounter
or may run into while processing data loads associated with them. As a result, most of my custom
exceptions have help messages that can guide you in times of trouble.

.. seealso::
   For a comprehensive review of all custom exceptions, have a look at the docs here:
   `core.custom_exceptions <core.html#module-core.custom_exceptions>`_

Configuration Issues
____________________

Configuration Management in this project is one of those areas that, I believe, will be easier as
newer solutions are introduced to make it slightly so. Nonetheless, reusable solutions must not rely on
hardcoded tweaks to shape behaviour, file handling or sensitive secrets. This is exactly why ``webmaster-seo-tools``
takes a modular approach to help as many users as possible with the least pain or without messing with the code.

.. tip::
   If you have not read about `Configuration Management <config_mgr.html#configuration-management>`_ yet,
   go ahead and check it out before going any further. It will give you a good understanding that will
   complement what follows.


Configuration File does not exist
#################################

Begin by creating your configuration files either via the setup script provided or copying and pasting
the templates provided in `Configuration Management <config_mgr.html#configuration-management>`_ into ``.ini`` files.
Configuration files must be located at the ``config`` folder in the ``core`` package.

.. note::
   Every time I use the word package in the context of file handling or placement, it has the same meaning as
   **directory** or **folder**. A Python package is a directory with a ``__init__.py`` file, but for practical
   and non-technical matters, it is just a regular path in your system. For example, the notation ``core.config``
   means *directory* ``config`` inside *directory* ``core``.

.. tip::
   Find a code example on how to generate your configuration file at the `Quick Start <home.html#quick-start>`_
   section of this documentation.

.. warning::
   With exception of file ``assets.ini``, **all** other configuration files are **required** for the correct
   execution of all tasks, bots, and integrations in this project. If one of them is missing, ``core.config_mgr``
   will not be able to load vital variables for the modules and a ``ConfigFileNotFound`` exception will be raised.


Assets not found
################

As it was discussed in `Configuration Management <config_mgr.html#configuration-management>`_,
file ``assets.ini`` is specific to the ``workflows.content_select`` bot and, while other workflows use
a huge portion of the logic implemented in it, ``core.config_mgr`` does not load this file when other
configuration files and classes are initialised. In other words, ``assets.ini`` is not essential to run other
programs and bots in ``webmaster-seo-tools`` and not having one does not crash programs that depend on
``workflows.content_select`` as a library.

.. attention::
   If you are getting an ``AssetsNotFoundError`` exception, it just means that you are trying to execute
   ``workflows.content_select`` as a program and there is no ``assets.ini`` file.
   On the other hand, if you really intend to run this program, contact MongerCash or go to their image
   banner page to get them.

   You only need to copy and paste the download link and set it up as outlined on
   `Configuration Management <config_mgr.html#configuration-management>`_

Invalid Configuration
#####################

Getting your values right is the most challenging part of manual configuration management.
In particular, True/False values, also called in the computing world ``boolean`` values.

.. tip::
   The most certain way to know if you need to set an option as True (yes) or False (No),
   are the words ``enabled`` and ``auto``. If you spot either, you know that those values are
   expected and the application won't work unless you set them.

   You can add them with or without capital letter or all capitals, however, do make sure
   the values are correct.

.. attention::
   Those options are only available in the ``workflows_config.ini`` in the ``core.config``
   package. If you try to run any of the applications in the ``workflows`` package without setting those
   options, you will get an undeniable ``InvalidConfiguration`` exception.

Let's talk about logs
#####################

Where to store logs and produce them is a problem that I take seriously.
Application logs gather information about your usage and the way variables and services interact with solutions here.

Logs are here simply because there is a possible configuration issue associated with them:
the ``UnavailableLoggingDirectory`` exception.

.. tip::
   Ensure all configurations are in place (again) including the ``logging_dirname`` option
   as this is the culprit here. This field has been already populated in the templates from
   `Configuration Management <config_mgr.html#configuration-management>`_ and its setup script.

.. attention::
   In case you are wondering, logs created by bots in the ``workflows`` package include,
   and are in no way limited to:

   1. User interaction with the solution (events)

   2. Custom post text, categories and slugs

   3. Machine Learning classifier suggestions

   4. Integration error messages or their associated payloads

   5. Warnings about missing identifiers tied to a service (e.g. WordPress taxonomies)

   6. Elapsed execution time

   7. Elapsed task time and retry offsets/attempts associated with routines

   8. Read and write (I/O) operations for critical files.

   9. Important data structures and number of iterations per prompt

   10. Debugging output from critical routines

   11. Environment variable assignment (not their content)

   12. User productivity with the solutions (number of processed records)

   13. Data dimensionality, database record density, and record count

   14. Formed payload for posts and image attributes (ALT Text, Description and Captions)

   15. Warnings associated with Connection Refused/Aborted exceptions and their library.

   16. Local time and date information

   17. Critical stops and handled exceptions

   It is vital to clarify that users hold complete autonomy with respect to whom they
   share logs with, which is different from, say, a telemetry system...

   ``webmaster_seo_tools`` does not collect this information for purposes of transmitting them in any manner or
   method that compromises users' privacy or autonomy.
   If you need help with an incidence, you can share the logs with anyone you trust.

.. tip::
   Logs can be used to coach your team and measure your productivity with the tool.
   Debugging output can aid troubleshooting as well as performance data can provide insights into
   what needs optimisations or reimplementation.

Data/Caching Integrity Issues
_____________________________

Data validation accounts for an enormous portion of the repeating load and network resource usage of this project and
its solutions.

HotFileSync
###########

HotFileSync is a solution that was developed with operational efficiency and scalability in mind. At the beginning,
the ``workflows.content_select`` bot had to work in conjunction with a primitive function in ``integrations.wordpress_api``
to get a fresh copy of ``wp_posts.json`` each time the data got dated and changes were not cached.

Although the algorithm is part of ``integrations.wordpress_api``, ``HotFileSync`` implemented an integrity verification
mechanism that could protect the local cache in case something goes wrong with the update procedures.
In the same way as ``integrations.wordpress_api``, it relies on the configuration file ``wp_config.json`` to verify that
the new data structure has the same number of elements which update request headers reported in the config file.

If, by any chance, the reported number of elements and the individual elements retrieved from WordPress do not match,
``HotFileSync`` will throw a ``HotFileSyncIntegrityError`` exception, the program crashes automatically as a result and the
current ``wp_posts.json`` remains untouched.

.. tip::
   As you soon will see, there are many reasons behind a ``HotFileSyncIntegrityError`` exception.
   You may want to try again as all ``workflows`` perform ``HotFileSync`` first thing, so just relaunch the bot.

   If that does not solve the problem, rebuild your local WordPress files:

   .. code-block:: console

      $ python3 -m integrations.wordpress_api --posts --yoast

   In case you are working with ``workflows.gallery_select``, replace ``--posts`` with ``--photos``.


.. seealso::
   Refer to `Quick Start <home.html#quick-start>`_ if you want to know more about the ``--yoast`` argument.


.. note::
   * **Why does the program have to crash if this happens?**

   A ``HotFileSyncIntegrityError`` is a rare occurrence and not good at all as it may indicate that
   either your ``wp_config.json`` or ``wp_posts.json`` are corrupted. An exception is raised because
   this data structure is critical to the successful execution of routines that manage content and
   ensure consistency in doing so.

   What would happen if you start pushing duplicated content to your site? What if important classification
   metadata is left out? *I bet you do not want to clean a mess afterwards, do you?*

   * **Is this not supposed to protect my cached data from corruption?**

   Yes and no. More precisely, it makes sure you are not using a corrupt copy of your ``wp_posts.json`` and
   that, in and of itself, is crucial to enforce consistency in your content management efforts.

   * **If the algorithm works, why would a locally cached copy of my posts get corrupted?**

   1. Your internet connection or a networking problem may interrupt the update procedure.

   2. A power outage may interrupt the runtime of the program.

   3. An intentional stop can happen while running the update (e.g. ``KeyboardInterrupt``)

   4. A critical stop of your Operating System (e.g. Kernel Panic)

Integration Issues
__________________

Bots in ``webmaster-seo-tools`` can communicate with services seamlessly, however, there are a couple of
exceptions that will crash the applications here, one being ``AccessTokenRetrivalError`` and the other
``RefreshTokenError``.

.. note::
   * **What does each exception mean?**

   Interestingly enough, ``AccessTokenRetrivalError`` is a configuration issue just like the ones
   I discussed at the beginning of this documentation page. It means that the integration authorisation flow
   is ready but it could not find the configuration fields to update them with the new tokens.
   As it was outlined in `Configuration Management <config_mgr.html#configuration-management>`_, those fields are
   located in the ``client_info.ini`` file at ``core.config``.

   ``RefreshTokenError`` suggests an issue with the integration service provider, it only means that the token
   could not be renewed. For this kind of issue, take a look at the failed request payload in the logs; it will
   tell you the exact cause of the problem. A common culprit is a locked account.

   As of now, only the X API uses these exceptions to notify users about common issues.

   * **How to solve a RefreshTokenError exception?**

   Once you have identified and solved the issue with your integration provider, then regenerate the tokens:

   .. code-block:: console

      $ python3 -m integrations.x_api --headless

Performance & Optimisation
__________________________
