.. highlight:: shell

.. _installation:
               
============
Installation
============

The roman-snpit-db is composed of two parts (both of which are in this archive).  The first is the database definition and server software.  If you need to install that, see TODO.  The second is the client software used to connect to an existing roman-snpit-db instance.  That's what this document is about.

Stable release
--------------

(Note: currently, as of this writing, there are no stable releases.)

To install roman-snpit-db, run this command in your terminal:

.. code-block:: console

    $ pip install roman-snpit-db

This is the preferred method to install roman-snpit-db, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for roman-snpit-db can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git@github.com:Roman-Supernova-PIT/roman_snpit_db.git

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/Roman-Supernova-PIT/roman_snpit_db/tarball/main

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ pip install .

If you would like to do an editable install:

.. code-block:: console

    $ pip install -e .
    $ pip install -e .[docs]  # install document build packages during install


.. _Github repo: https://github.com/Roman-Supernova-PIT/roman_snpit_db
.. _tarball: https://github.com/Roman-Supernova-PIT/roman_snpit_db/tarball/master
