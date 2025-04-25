import re
from urllib.parse import urlparse
import bs4
from bs4 import BeautifulSoup
from collections import Counter
import os
import string



# load the stopwords
def load_stopwords(file_path='stopwords.txt'):
    try:
        with open(file_path, 'r') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Using empty stopwords set.")
        return set()


STOP_WORDS = load_stopwords()

# files to store data for report
UNIQUE_PAGES_FILE = 'unique_pages.txt'
WORD_COUNTS_FILE = 'word_counts.txt'
COMMON_WORDS_FILE = 'common_words.txt'
SUBDOMAINS_FILE = 'subdomains.txt'

# allowed domains and paths
ALLOWED_DOMAINS = {
    'ics.uci.edu',
    'cs.uci.edu',
    'informatics.uci.edu',
    'stat.uci.edu',
    'today.uci.edu'
}
ALLOWED_PATH_PREFIX = '/department/information_computer_sciences'

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    #use beautifulsoup to scrape information and parse

    #store

    return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        #check for calendar pages which are traps
        #store number of unique pages, longest page, 50 most common terms, subdomains each in a file so information is accessible after program terminates
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        if parsed.scheme not in set(["http", "https"]):
            return False

        # check if it is an allowed domain
        in_allowed_domain = False
        for allowed_domain in ALLOWED_DOMAINS:
            if domain == allowed_domain or domain.endswith(f'.{allowed_domain}'):
                in_allowed_domain = True
                break
        if not in_allowed_domain:
            return False

        if domain == 'today.uci.edu' and not path.startswith(ALLOWED_PATH_PREFIX):
            return False

        # avoids traps posed by calendars
        if re.search(r'(calendar|event|\d{4}-\d{2}-\d{2})', path):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
