import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from collections import Counter
import sys
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


def tokenize(text):
    tokens = Counter()
    # Convert to lowercase and split by non-alphanumeric characters
    words = re.findall(r'\b[a-z0-9]+\b', text.lower())
    for word in words:
        if word not in STOP_WORDS and len(word) > 1:  # Ignore single characters
            tokens[word] += 1
    return tokens


# files to store data for report
UNIQUE_PAGES_FILE = 'unique_pages.txt'
WORD_COUNTS_FILE = 'word_counts.txt'
COMMON_WORDS_FILE = 'common_words.txt'
SUBDOMAINS_FILE = 'subdomains.txt'
ERROR_FILE = 'crawler_errors.txt'

# variables to collect data for report
unique_pages = set()
word_frequencies = Counter()
subdomain_pages = {}
longest_page = {'url': '', 'word_count': 0}

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
    global unique_pages, word_frequencies, subdomain_pages, longest_page

    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        if 600 <= resp.status <= 606:
            error_msg = resp.error if resp.error else "No error message provided"
            with open(ERROR_FILE, 'a') as f:
                f.write(f"Error for {url}: Status {resp.status}, Error: {error_msg}\n")
        return []

    # defragment URL for uniqueness
    defragged_url, _ = urldefrag(resp.url)
    if defragged_url in unique_pages:
        return []
    unique_pages.add(defragged_url)

    try:
        # use beautifulsoup to parse page
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        unique_pages.add(resp.url)

        #TODO: extract subdomain and update the subdomain_pages
        parsed_url = urlparse(resp.url)
        subdomain = parsed_url.netloc.lower()  # lower to normalize
        if subdomain not in subdomain_pages.keys():
            subdomain_pages[subdomain] = set()
        else:
            subdomain_pages[subdomain].add(resp.url)

        #TODO: extract text
        text = [text for text in soup.stripped_strings]

        #TODO: exclude stop words when counting words
        tokens = tokenize(text)     
        # would need to compute the number of word frequencies across ALL crawled pages
        word_frequencies = word_frequencies + Counter(tokens)
        curr_word_count = sum(word_frequencies.values())

        #TODO: update longest page if needed
        if curr_word_count > longest_page["word_count"]:
            longest_page["url"] = resp.url
            longest_page["word_count"] = curr_word_count

        #TODO: extract hyperlinks
        links = []
        for link in soup.find_all('a'):
            links.append(link.get('href'))

        #TODO: call method to save to reports save_data()
        # save_data()
        return links

    except Exception as e:
        print(f"Error {url}: {e}")
        return []


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        #TODO: Check for other criteria for infinite traps and pages with no info
        parsed = urlparse(url)
        domain = parsed.netloc.lower() # extracts the domain
        path = parsed.path.lower() # extracts the path
        if parsed.scheme not in {"http", "https"}:
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

        #check for high quality pages (over 100 text)


        if 'download' in path or 'attachment' in path:
            return False

        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False

        return True

    #TODO: don't know if this needs to be fixed
    except TypeError:
        print("TypeError for ", parsed)
        raise


def save_data():
    # manage global vars
    global unique_pages, word_frequencies, subdomain_pages, longest_page
    with open(UNIQUE_PAGES_FILE, 'w') as f:
        f.write(f"Total unique pages: {len(unique_pages)}\n")
        for page in sorted(unique_pages):
            f.write(f"{page}\n")

    with open(WORD_COUNTS_FILE, 'w') as f:
        f.write(f"Longest page: {longest_page['url']}\n")
        f.write(f"Word count: {longest_page['word_count']}\n")

    with open(COMMON_WORDS_FILE, 'w') as f:
        f.write("50 most common words:\n")
        for word, count in word_frequencies.most_common(50):
            f.write(f"{word}: {count}\n")

    with open(SUBDOMAINS_FILE, 'w') as f:
        f.write("Subdomains and page counts:\n")
        for subdomain in sorted(subdomain_pages.keys()):
            f.write(f"{subdomain}, {len(subdomain_pages[subdomain])}\n")


#################################
# TEST # cursorai


class MockResponse:
    def __init__(self, status, content, url):
        self.status = status
        self.raw_response = self.RawResponse(content, url)
        self.url = url
    
    class RawResponse:
        def __init__(self, content, url):
            self.content = content
            self.url = url

# Create a mock response to simulate an HTTP request
'''
mock_html_content = ///
<html>
    <body>
        <a href="https://example.com/page1">Link 1</a>
        <a href="/page2">Link 2</a>
        <a href="https://example.com/page3">Link 3</a>
        
    </body>
</html>
///
mock_resp = MockResponse(status=200, content=mock_html_content.encode('utf-8'), url="https://example.com")


def main ():
    print("start")
    print(extract_next_links(".ics.uci.edu", mock_resp))



if __name__ == "__main__":
    main()
'''