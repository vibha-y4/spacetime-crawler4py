import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import utils


def fix_URL(url : str, href : str):
    result = None
    if href.startswith('#') or href.startswith('tel') or href.startswith('mailto'):
        result =  None
    elif href.startswith('//'):
        result = 'https:' + href
        print(result)
    elif href.startswith('/'):
        root = re.match(r'^(https?://[^/]+)', url)
        result = f'{root.group(1)}{href}'
    return result
    
    
# load the stopwords
def load_stopwords(file_path='stopwords.txt'):
    try:
        with open(file_path, 'r') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Using empty stopwords set.")
        return set()


STOP_WORDS = load_stopwords()


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
    if resp.error:
        return list()
    else:
        page_content = resp.raw_response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        link_content = soup.find_all('a')
        links = set()
        for link in link_content:
            if link.has_attr('href'):
                href = link['href']
                link = fix_URL(url, href)
                if link is not None:
                    #print(link)
                    links.add(link)
    #store

    return list(links)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        #check for calendar pages which are traps
        #store number of unique pages, longest page, 50 most common terms, subdomains each in a file so information is accessible after program terminates
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
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
