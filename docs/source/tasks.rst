tasks package
=============

The reason behind the separation of ``tasks`` and ``integrations`` is not the point that makes them converge,
in that both packages deal with data processing and gathering, more specifically, data coming from the internet;
nevertheless, the means in which each package gathers data makes a case for differentiation.

``tasks`` accesses pieces of data that are not supposed to be retrieved programmatically, so in this case each module
implements different techniques for web automation and parsing/modelling.

``tasks`` harnesses the power of the ``Selenium`` webdriver automation suite to interact with web elements and collaborate with local routines that will turn
all the details into meaningful information.

.. note::
   In an effort to optimise functionality in web element interaction, the routines in this package use a combination of
   HTML identifiers and XPath routes that have been tested in both Firefox (Gecko) and Chrome (Blink).

.. tip::
   ``headless`` automation is fully compatible with this package; its coordinating workflow ``workflows.update_mcash_chain``
   creates a browser instance that can follow instructions in the background, all without looking at the process.

.. seealso::
   If you want to see how ``headless`` mode integrates as a command line argument or how to change your
   web driver before executing your tasks, take a look at `Get to Know the Bots <home.html#get-to-know-the-bots>`_
   specially ``update_mchash_chain``.

   If you want to expand your knowledge about common command line arguments
   used in this project, head over to `integrations package <integrations.html#integrations-package>`_






Submodules
----------

tasks.mcash\_dump\_create module
--------------------------------

.. automodule:: tasks.mcash_dump_create
   :members:
   :undoc-members:
   :show-inheritance:

tasks.mcash\_scrape module
--------------------------

.. automodule:: tasks.mcash_scrape
   :members:
   :undoc-members:
   :show-inheritance:

tasks.parse\_txt\_dump module
-----------------------------

.. automodule:: tasks.parse_txt_dump
   :members:
   :undoc-members:
   :show-inheritance:

tasks.sets\_source\_parse module
--------------------------------

.. automodule:: tasks.sets_source_parse
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: tasks
   :members:
   :undoc-members:
   :show-inheritance:
