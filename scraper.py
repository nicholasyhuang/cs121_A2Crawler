import re
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import time

def scraper(url, resp):
    links = extract_next_links(url, resp)

    #TODO process resp.raw_response.content .. ? and update wordcounts + longest page into save file
    #stopwords should probably be ignored in this step
    

    robotrules=dict()
    return [link for link in links if (is_valid(link) and robotsCheck(link, robotrules))]
    #robotsCheck may be moved to is_valid, manual reading file each time (slower ...)

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
    print(type(resp.raw_response.content))
    page = resp.raw_response.content.decode("utf-8")
    linkmatches = re.findall("href=[\"'].*?[\"']", page)
    links = list()
    robotrules = dict() #TODO remove

    print("############### URLS SCRAPED ##############") #TODO remove
    for linkmatch in linkmatches:
        scrapedurl = re.search("[\"'](.*)[\"']", linkmatch).group(1)
        #TODO remove the fragment portion of URL
        #removes fragment
        #psurl = urlparse(scrapedurl)
        #scrapedurl = psurl.scheme + "://" + psurl.netloc + psurl.path + psurl.query
        #links.append(scrapedurl) #add url to links
        #TODO remove this block, is for testing only
        if(robotsCheck(scrapedurl, robotrules) and is_valid(scrapedurl)):
            print("VALID:", scrapedurl)
        else:
            print("INVALID:", scrapedurl)
    print("############### END URLS SCRAPED #################") #TODO remove

    print("=============RESPONSE.CONTENT==============: \n", page, 
          "\n================END RESPONSE.CONTENT==================\n") #TODO remove
    
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        #TODO check url for strange things like repetitive paterns and query parameters here
        #if not robotsCheck(url):
        #    return False
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

def robotsCheck(url, robotrules=dict()): 
    if not url:
        return False
    parsed = urlparse(url)
    if not parsed.hostname: 
        return False
    
    if("cs.uci.edu" in parsed.hostname):
        robotspath = "robots/cs.uci.edu.robots.txt"
    elif "ics.uci.edu" in parsed.hostname:
        robotspath = "robots/ics.uci.edu.robots.txt"
    elif "informatics.uci.edu" in parsed.hostname:
        robotspath = "robots/informatics.uci.edu.robots.txt"
    elif "stat.uci.edu" in parsed.hostname:
        robotspath = "robots/stat.uci.edu.robots.txt"
    else: #the url is NOT one of the things we can crawl
        return False 

    try:
        robotsfile = open(robotspath, "r")
        robotstext = robotsfile.readlines()
    except:
        print("COULDN'T OPEN FILE PATH -", robotspath)
        return False
    
    if parsed.hostname in robotrules.keys():
        parser = robotrules[parsed.hostname]
    else:
        parser = RobotFileParser()
        parser.parse(robotstext)
        robotrules[parsed.hostname] = parser
    return parser.can_fetch("*", url)

    


