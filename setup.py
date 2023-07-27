from setuptools import setup, find_packages

# This is a "single-module distribution"

from export_help_scout_docs import __version__

setup(
    name='export_help_scout_docs',
    version=__version__,
    url='https://github.com/adamwolf/export-help-scout-docs.git',
    author='Adam Wolf',
    author_email='adamwolf@feelslikeburning.com',
    description='Export Help Scout Docs',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'export_help_scout_docs=export_help_scout_docs:main',
        ],
    },
)