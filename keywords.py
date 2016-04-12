import operator
import requests
import unicodedata

from bs4 import BeautifulSoup
from collections import defaultdict

import app_settings
import exclusions


class Keywords(object):

    def __init__(self):
        self.url = "https://api-v2.themuse.com/jobs"

        self.listings = []
        self.keywords = defaultdict(int)


    def _parse_soup(self, soup):
        """
        Params: 
            soup (bs4.BeautifulSoup): BeautifulSoup object containing raw html from post

        Return: Text as list of words, with punctuation / special characters removed
        """
        soup = ' '.join(s for s in soup.stripped_strings)

        # beautifulsoup uses unicode, which makes stripping out unwanted punctuation difficult. 
        # Since everything's in English (for now), convert back to ascii. 
        if type(soup) != str:
            soup = unicodedata.normalize("NFKD", soup).encode("ascii", "ignore")

        punctuation = exclusions.punctuation
        soup = soup.translate(None, punctuation)

        # Special case for "/"
        soup = soup.replace("/", " ")

        soup = soup.split()

        return soup


    def get_listings(self, request_params, section):
        """
        Params: 
            request_params (dict): Query parameters
            section (str): Muse JSON attribute containing the relevant data

        Iterates through all the pages of the query and updates self.listing with listings
        """
        try:
            # Get page count:
            res = requests.get(self.url, params=request_params, timeout=5)
            if res.status_code == 200:
                res = res.json()

                page_count = res.get("page_count")

            # Loop through pages
            # TODO: Better error handling here, such that one call dying doesn't ruin the whole thing
            for p in range(2, page_count + 1):
                request_params["page"] = p

                res = requests.get(self.url, params=request_params, timeout=5)

                if res.status_code == 200:
                    res = res.json()
                    res = res.get("results")

                    for r in res:
                        self.listings.append(BeautifulSoup(r.get(section), "html.parser"))

        # TODO: Handle these better
        except ValueError:
            # Response isn't JSON
            print "There was an error retrieving posts."

        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            print "Getting posts is taking too long, please try again later"


    def get_keywords(self, category=None):
        """
        Params:
            category (str): Job category

        Runs through flow from setting up parameters to query, to storing keywords in self.keywords
        """

        request_params = {
            "api_key": app_settings.API_KEY,
            "page": 1,
            "flexible": True,
        }

        if category:
            request_params["category"] = category

        self.get_listings(request_params, "contents")

        exclude_words = exclusions.exclude_words

        for l in self.listings:
            parsed = self._parse_soup(l)

            for word in parsed:
                word = word.lower()
                if word not in exclude_words:
                    self.keywords[word] += 1


    def top_keywords(self, count):
        """
        Params: 
            count (int): Number of top keywords to return

        Returns: self.keywords dict sorted by value in reverse order and sliced by count
        """
        return sorted(self.keywords.items(), key=operator.itemgetter(1), reverse=True)[:count]


if __name__ == "__main__":
    k = Keywords()

    print ">>> Find Keywords"

    print ">>> Please enter a category, for a list of valid categories enter 'list':"
    category = raw_input()

    while (category not in app_settings.CATEGORIES) or (category == "list"):
        if category == "list":
            for item in app_settings.CATEGORIES:
                print '- ' + item
            category = raw_input()

        elif category not in app_settings.CATEGORIES:
            print ">>> Not a valid category, please reenter: "
            category = raw_input()

    print ">>> Getting posts..."
    k.get_keywords(category)

    print ">>> How many top keywords would you like to see? Type 'quit' to quit at any time:"
    num = raw_input()
    while num != "quit":
        try: 
            print ">>> Sorting keywords..."
            keywords = k.top_keywords(int(num))
            for w, c in keywords:
                print w, "(" + c + ")"

            print ">>> "
            num = raw_input()

        except ValueError:
            print ">>> Invalid input, please enter a number or 'quit':"
            num = raw_input()


