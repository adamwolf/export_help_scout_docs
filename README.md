# export_help_scout_docs

*Export documents from Help Scout Docs as JSON files*

## Requirements
* Python 3 (probably something like 3.6 or newer?)

## Usage

You need an API key for Help Scout Docs. There are instructions at 
https://developer.helpscout.com/docs-api/#your-api-key.

export_help_scout_docs looks for the API key in the environment variable `HELPSCOUTAUTH` and in the argument 
`--token`.

Running `export_help_scout_docs --token <your API key>` will print out the Help Scout Docs collections the API key
can access.  Use the ID of the collection you want to export as the argument to `--collection`, like this:

```
export_help_scout_docs --token <your API key> --collection <collection ID>
```

This will create a new directory and fill it with one JSON file per document.

Run `export_help_scout_docs --help` for more information.

## Installation

export_help_scout_docs doesn't require any libraries that aren't included with Python 3.

If you're not sure how to install it, I suggest installing with [pipx](https://pypa.github.io/pipx/). Once you've got 
pipx installed, you can install expand_help_scout_docs like this:

```
pipx install git+https://github.com/adamwolf/export_help_scout_docs.git
```

pipx installs each package into its own little area, just for you, where you don't have to worry about it messing with 
any system-wide or even user-wide Python dependencies.

## Building an executable
I don't really know PyOxidizer, but you can use it to build a single-file executable:

```
pip install pyoxidizer
pyoxidizer build
```