#!/usr/bin/env python3
import argparse
import base64
import json
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import urllib
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(message)s')

REQUEST_DELAY = 1  # seconds

__version__ = "0.0.1"


def safe_get(url, params=None, auth=None, retries=2):
    """
    Perform a GET request with retries.

  :param url: The URL to fetch.
  :param params: Optional request parameters.
  :param auth: Optional authentication tuple (username, password).
  :param retries: The number of attempts to make before giving up.
  :return: The JSON response data, or None if the request failed.
  """
    for attempt in range(retries):
        try:
            if params:
                url += '?' + urllib.parse.urlencode(params)

            request = Request(url)

            if auth:
                username, password = auth

                if password is None:
                    password = ''
                encoded_token = base64.b64encode(f"{username}:{password}".encode('ascii'))
                request.add_header('Authorization', 'Basic %s' % encoded_token.decode("ascii"))
                # Note, the HTTPBasicAuthHandler method requires the server to send a Www-Authenticate header,
                # which many don't, so...

            response = urlopen(request)

            data = json.loads(response.read().decode())
            return data
        except HTTPError as e:
            logging.error(f"Request error: {e}")
            if attempt < retries - 1:
                time.sleep(REQUEST_DELAY)
                continue
            else:
                raise e

    raise Exception  # Should never get here


def help_scout_get(url, params=None, token=None):
    if token:
        auth = (token, "x")
    else:
        auth = None

    return safe_get(url, params=params, auth=auth)


def export_help_scout_docs(token, collection_id, directory_path):
    logging.info("Starting Help Scout Docs export")
    article_ids = get_article_ids(token, collection_id)
    logging.info(f"Found {len(article_ids)} article IDs")
    articles = fetch_articles(article_ids, directory_path, token)
    logging.info(f"Saved all {len(articles)} articles into {directory_path}")


def unique_filename(directory_path, base_filename, extension):
    suffix = ""
    counter = 1

    # Keep trying new filenames until we find one that doesn't exist
    while (directory_path / f"{base_filename}{suffix}{extension}").exists():
        suffix = f"-{counter}"
        counter += 1

    return directory_path / f"{base_filename}{suffix}{extension}"


def fetch_articles(article_ids, directory_path, token):
    """
  Fetch and save articles.
  :param article_ids: ids of articles to fetch
  :param directory_path: Path to directory to save articles in
  :param token: Help Scout API token
  :return: the articles
  """

    articles = []
    logging.debug(f"Creating directory {directory_path}")
    try:
        directory_path.mkdir(exist_ok=False)
    except FileExistsError:
        logging.error(f"Directory {directory_path} already exists")
        exit(1)

    for i, article_id in enumerate(article_ids):
        logging.info(f"Getting article {article_id} ({i + 1}/{len(article_ids)})")
        time.sleep(REQUEST_DELAY)
        url = f"https://docsapi.helpscout.net/v1/articles/{article_id}"
        data = help_scout_get(url, token=token)
        article = data["article"]
        article_path = unique_filename(directory_path, article["slug"], ".json")
        logging.debug(f"Saving article to {article_path}")
        with open(article_path, 'w') as f:
            json.dump(data, f, indent=2)
    return articles


def get_paged_help_scout_entities(token, url, entity_name):
    current_page = None
    total_pages = None
    next_page = 1
    entities = []
    while current_page is None or current_page < total_pages:
        logging.info(f"Getting page {next_page}")
        data = help_scout_get(url, params={"page": next_page}, token=token)
        current_page = int(data[entity_name]["page"])
        total_pages = int(data[entity_name]["pages"])
        next_page = current_page + 1

        for entity in data[entity_name]["items"]:
            entities.append(entity)
        time.sleep(REQUEST_DELAY)
    return entities


def get_article_ids(token, collection_id):
    """
    Fetch all the article IDs in a collection.
    :param: token: The authentication token.
    :param: collection_id: The ID of the collection to fetch.
    :return: A list of article IDs.
    """
    # We can list all the articles, but that listing doesn't contain the text,
    # so we grab the IDs to later fetch them one by one
    logging.info(f"Getting article IDs for collection {collection_id}")
    articles = get_paged_help_scout_entities(token,
                                             f"https://docsapi.helpscout.net/v1/collections/{collection_id}/articles",
                                             "articles")
    article_ids = [article["id"] for article in articles]
    return article_ids


def get_collections(token):
    url = f"https://docsapi.helpscout.net/v1/collections"
    logging.info("Getting collections")
    collections = get_paged_help_scout_entities(token, url, "collections")
    return collections


def main():
    parser = argparse.ArgumentParser(description="Export from Help Scout Docs")
    # add version
    parser.add_argument("--token",
                        help="Please put the API token into the HELPSCOUTAUTH environment variable if possible")
    parser.add_argument("--collection",
                        help="Help Scout collection ID.  If this isn't set, try to print a list of collections.")
    parser.add_argument("--output_dir",
                        help="The directory where the backup will be saved. Defaults to a new directory in the "
                             "current directory named 'help-scout-export-<current datetime>'.")
    parser.add_argument('-v', '--version', action='version', version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    token = args.token or os.getenv("HELPSCOUTAUTH")
    if token is None:
        raise parser.error(message="HELPSCOUTAUTH environment variable (or --token) must be set.")

    if args.collection is None:
        logging.warning("No collection specified")
        logging.info("Fetching collection information")
        collections = get_collections(token)
        if not collections:
            raise parser.error(message="No collections found for token.")
        else:
            logging.info("Found collections:")
            for collection in collections:
                logging.info(f"{collection['id']}: {json.dumps(collection, indent=2)}")
            logging.info("Please specify a collection ID with --collection")
            exit(1)

    if args.output_dir is None:
        directory_name = f"help-scout-export-{datetime.now().isoformat()}"
        logging.debug(f"No output directory specified, defaulting to {directory_name}")
        directory_path = Path(directory_name)
    else:
        directory_path = Path(args.output_dir)

    if directory_path.exists():
        raise parser.error(message=f"Output directory {directory_path} already exists.")

    export_help_scout_docs(token, args.collection, directory_path)


if __name__ == '__main__':
    main()
