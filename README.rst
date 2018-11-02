Hermes
======

An IRC bot built for the next generation of Gazelle sites. It takes ideas and inspiration from
[zookeeper](https://github.com/phracker/zookeeper), while providing a much more secure, stable, and extendable
platform from which someone can build for their needs.

The bot is written for Python 3.

Installation
------------

To install, run the setup.py file::

    python3 setup.py install


This will install the bot, and its dependencies, and create a script in /usr/local/bin (or wherever Python is
setup to create new bin files) to run the bot through the "hermes" command.

Usage
-----

Running hermes::

    bin/hermes

Hermes primarily runs itself out of the ~/.hermes directory of the user that is running it. Inside, it expects to
find a `config.yml` file (explained below), and will log output (if run under the -v or -vv flags) and also
load any `.py` files found in `~/.hermes/modules` directory. The bin script will also create a `hermes.pid` file
in that directory to prevent multiple instances of the bot from running.


Configuration
-------------

The bot is managed through the `config.yml` file (a sample one is provided at `config.yml.sample`). It currently
does not make sure that you have all settings set appropriately, so do take care. You just need to copy the example
to `~/.hermes/config.yml`, and change it as necessary. It should be relatively straightforward to do.

