import re
from bs4 import BeautifulSoup
import pickle
import os
from hashlib import md5
from urllib.parse import urlparse


#performs simhash on tokenized text (output of tokenize()), returns list of 1's and 0's, the simhash of the document
def simhash(tokenlist):
    SIMHASH_FINGERPRINT_SIZE = 64 #must be less than 128
    votes = [0]*SIMHASH_FINGERPRINT_SIZE

    for token in tokenlist:
        tokenhash = bin(int.from_bytes(md5(str.encode(token)).digest(), 'little'))[-SIMHASH_FINGERPRINT_SIZE:]
        for i in range(SIMHASH_FINGERPRINT_SIZE):
            if(tokenhash[i]=='0'):
                votes[i]+=1
            else:
                votes[i]-=1
    
    for i in range(SIMHASH_FINGERPRINT_SIZE):
        if votes[i] > 0:
            votes[i] = 1
        elif votes[i] == 0:
            votes[i] = i%2
        else:
            votes[i] = 0
    return votes
    #stopwords should already be removed for tokenized_text !!!

    #quoting google "features are computed using standard IR techniques like tokenization, case folding, stop-word removal etc."
    #set of weighted featuers -> high dimensional vector, with 1 dimension per unique feature in all documents taken together
    #simhash can transform high dimensional vector into f-bit fingerprint where f is 64 bit
    #tokenize, then remove stopwords
    #take (weighted) features, hash each feature into 64 bits
    #features will "vote" and return 64 bits of a hash
    #hamming distances of 5-10 are good (start with 5)
    
def similarHashes(simhash1, simhash2): #are they similar hashes? compares 2 simhashes
    HAMMING_DISTANCE = 5
    diff = 0
    for i in range(len(simhash1)):
        if simhash1[i]!=simhash2[i]:
            diff+=1
            if(diff>=HAMMING_DISTANCE): #if there r more than 5 differences, they are NOT similar hashes
                return False
    return True
    

#cleans stopwords from tokenlist lol
def cleanStopwords(tokenlist):
    cleanlist = list()
    stopwords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
                 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 
                 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 
                 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 
                 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 
                 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 
                 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 
                 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 
                 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 
                 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
                 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
                 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 
                 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 
                 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 
                 'don', 'should', 'now'])
    for token in tokenlist:
        if not token in stopwords:
            cleanlist.append(token)
    return cleanlist

def tokenize(text):
    delimcharacters= ' ,.!?:;/—|\\+=}{{}}\n\t\r\f\v'
    delims = set()
    for ch in delimcharacters:
        delims.add(ch)

    alphnum = set()
    alphanumeric = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'
    for ch in alphanumeric:
        alphnum.add(ch)
    
    token=''
    tokenlist = list()
    #c = f.read(1)
    for c in text:
        if(c in delims and token!=''):
            tokenlist.append(token)
            token = ''
        elif c in alphnum: 
            token+=c.lower()

        #c = f.read(1)
    if token!='':
        tokenlist.append(token)

    return tokenlist

def updateMostTokens(tokenlist, url):
    try:
        with open('Logs/mosttokens.log', 'rb') as f:
            if(os.path.getsize('Logs/mosttokens.log')==0):
                freq = dict()
            else:
                freq = pickle.load(f)
            f.close()
            
    except FileNotFoundError:
        f=open('Logs/mosttokens.log', 'w')
        f.close()
        freq=dict()

    if "most.tokens" in freq:
        if(len(tokenlist) > freq['most.tokens']):
            freq['most.tokens'] = len(tokenlist)
            freq['most.url'] = url
        #freq['most.tokens'] = max(len(tokenlist), freq['most.tokens'])
    else:
        freq['most.tokens'] = len(tokenlist)
        freq['most.url'] = url
    
    with open('Logs/mosttokens.log', 'wb') as f:
        pickle.dump(freq, f)
        f.close()

def updateDomainCnt(url):
    try:
        with open('Logs/subdomain_counts.log', 'rb') as f:
            if(os.path.getsize('Logs/subdomain_counts.log')==0):
                counts = dict()
            else:
                counts = pickle.load(f)
            f.close()
    except FileNotFoundError:
        open('Logs/subdomain_counts.log', 'w').close()
        counts = dict()
    
    parsed = urlparse(url)
    if(re.match(r'.*\.ics.uci.edu.*', url)):
        domain = parsed.scheme + "://" + parsed.hostname
        if domain in counts:
            counts[domain] += 1
        else:
            counts[domain] = 1
    with open('Logs/subdomain_counts.log', 'wb') as f:
        pickle.dump(counts, f)
        f.close()
    return counts


def compsaveWordFrequencies(tokenlist): #computes and saves word frequencies
    try:
        with open('Logs/wordfreqs.log', 'rb') as f:
            if(os.path.getsize('Logs/wordfreqs.log')==0):
                freq = dict()
            else:
                freq = pickle.load(f)
            f.close()
    except FileNotFoundError:
        f=open('Logs/wordfreqs.log', 'w')
        f.close()
        freq = dict()


    for token in tokenlist:
        if token in freq:
            freq[token]+=1
        else:
            freq[token] = 1
    
    with open('Logs/wordfreqs.log', 'wb') as f:
        pickle.dump(freq, f)
        f.close()
    return freq

#takes in raw html and extracts the text, returning it in a string
def cleanHtml(rawtext):
    soup = BeautifulSoup(rawtext, "html.parser")
    cleanedtext = soup.get_text(separator=' ', strip=True)
    return cleanedtext

def loadSimHashes():
    simhashes = list()
    try:
        with open('Logs/simhashes.log', 'rb') as f:
            if(os.path.getsize("Logs/simhashes.log")==0):
                return simhashes
            simhashes = pickle.load(f)
            f.close()
    except FileNotFoundError:
        open('Logs/simhashes.log', 'w').close()
    return simhashes

def saveSimHash(simhashes):
    with open('Logs/simhashes.log', 'wb') as f:
        pickle.dump(simhashes, f)
        f.close()
    

def clearLogs():
    print("CLEARING LOGS.....", end="")
    open("Logs/wordfreqs.log", "w").close()
    open('Logs/simhashes.log', 'w').close()
    open('Logs/subdomain_counts.log', 'w').close()
    print("LOGS CLEARED!")

if __name__ == '__main__':

    with open('Logs/wordfreqs.log', 'rb') as f:
        h = pickle.load(f) 
        sorted_wordfreqs = dict(sorted(h.items(), key=lambda item: item[1], reverse=True))
        print(sorted_wordfreqs)
        f.close()
    with open('Logs/mosttokens.log', 'rb') as f:
        h = pickle.load(f)
        print(h)
        f.close()
    with open('Logs/simhashes.log', 'rb') as f:
        h = pickle.load(f)
        print(len(h))
        f.close()
    with open('Logs/subdomain_counts.log', 'rb') as f:
        h = pickle.load(f)
        print(h)
        f.close()
    
