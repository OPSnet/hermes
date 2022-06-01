from setuptools import setup
import sys

from hermes.hermes import __version__

if sys.version_info < (3, 5):
    raise SystemExit("hermes can only be installed using Python 3.5+")

setup(
    name='hermes',
    author="itismadness",
    version=__version__,
    description="An IRC bot designed to be used by sites running the Gazelle tracker software.",
    packages=['hermes'],
    entry_points={'console_scripts': ['hermes = hermes:run_hermes']},
    requires=[
        'irc',
        'PyYAML',
        'httpx',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Chat :: Internet Relay Chat'
    ]
)
