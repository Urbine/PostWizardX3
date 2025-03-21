integrations package
====================

As mentioned in the project's home, ``integrations`` deals with public services or APIs that
deliver data to the applications and bots in this project, which means that any service provider with
an interface to fetch details will be added here.

Integrations in this module include:

1. WordPress JSON REST API

2. TubeCorporate Feeds (VJAV, Desi Tube)

3. AdultNext API (Abjav)

4. X (formerly Twitter) API

5. Telegram BotFather API

6. FapHouse API

.. tip::
   All integrations implemented in this module have Command Line Interface (CLI) that makes it
   easier to use them as standalone programs.

   Try passing in the ``--help`` parameter to any of the modules in order to gain a broader understanding
   on how a certain integration can help you.

   .. code:: console

      $ python3 -m integrations.wordpress_api --help


.. note::
   You may notice that all integrations have a ``--parent`` argument; however,
   if you run the applications as standalone modules, there is little to no usage for
   this one since functions in the project have been optimised to deal with different paths in order to
   locate resources within the working directory and its parent.
   *For this reason, you may safely ignore it.*

.. tip::
   Other common arguments are ``--folder`` and ``--extension``.
   In the case of folders, you can provide the name of such and functions from the ``core``
   package will locate it for you. In the same way, file extension with or without the "." are allowed.
   For example, ``--extension .json`` and ``--extension json`` are equivalent.

.. seealso::
   You can find code examples for modules in this package here:
   `Quick Start <home.html#quick-start>`_

Submodules
----------

integrations.adult\_next\_api module
------------------------------------

.. automodule:: integrations.adult_next_api
   :members:
   :undoc-members:
   :show-inheritance:

integrations.botfather\_telegram module
---------------------------------------

.. automodule:: integrations.botfather_telegram
   :members:
   :undoc-members:
   :show-inheritance:

integrations.brave\_search\_api module
--------------------------------------

.. automodule:: integrations.brave_search_api
   :members:
   :undoc-members:
   :show-inheritance:

integrations.callback\_server module
------------------------------------

.. automodule:: integrations.callback_server
   :members:
   :undoc-members:
   :show-inheritance:

integrations.fhouse\_api module
-------------------------------

.. automodule:: integrations.fhouse_api
   :members:
   :undoc-members:
   :show-inheritance:

integrations.tube\_corp\_feeds module
-------------------------------------

.. automodule:: integrations.tube_corp_feeds
   :members:
   :undoc-members:
   :show-inheritance:

integrations.url\_builder module
--------------------------------

.. automodule:: integrations.url_builder
   :members:
   :undoc-members:
   :show-inheritance:

integrations.wordpress\_api module
----------------------------------

.. automodule:: integrations.wordpress_api
   :members:
   :undoc-members:
   :show-inheritance:

integrations.x\_api module
--------------------------

.. automodule:: integrations.x_api
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: integrations
   :members:
   :undoc-members:
   :show-inheritance:
