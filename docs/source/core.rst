core package
============

``core`` contains reusable implementations and configuration files that control:

1. Authentication and project-wide secrets.

2. Task constants.

3. Asset and behaviour variables for workflows.

4. Custom exceptions.

5. Helper utilities.

The main ideas behind the concept of configuration manager that I adopted is modularity,
adaptability and security. All configuration files are parsed and delivered to other modules
by using special factory functions with immutable objects that can't be modified during runtime.

Advantages to this approach are the ability to modify values without messing with the code to
personalize the experience while using the tools. Data gets validated within the application to ensure
that behaviour is not unexpected and exceptions containing helpful messages contribute to effective troubleshooting.


Submodules
----------

core.config\_mgr module
-----------------------

.. automodule:: core.config_mgr
   :members:
   :undoc-members:
   :show-inheritance:

core.custom\_exceptions module
------------------------------

.. automodule:: core.custom_exceptions
   :members:
   :undoc-members:
   :show-inheritance:

core.helpers module
-------------------

.. automodule:: core.helpers
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: core
   :members:
   :undoc-members:
   :show-inheritance:
