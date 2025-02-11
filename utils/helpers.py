import re
from bs4 import BeautifulSoup
import pickle
import os

#performs simhash on tokenized text (output of tokenize()), returns int simhash
def simhash(tokenized_text):
    SIMHASH_FINGERPRINT_SIZE = 64
    #first remove stop words !!!
    #quoting google "features are computed using standard IR techniques like tokenization, case folding, stop-word removal etc."
    #set of weighted featuers -> high dimensional vector, with 1 dimension per unique feature in all documents taken together
    #simhash can transform high dimensional vector into f-bit fingerprint where f is 64 bit
    #tokenize, then remove stopwords
    #take (weighted) features, hash each feature into 64 bits
    #features will "vote" and return 64 bits of a hash
    #hamming distances of 5-10 are good (start with 5)
    pass


def tokenize(text):
    delimcharacters= ' ,.!?:;/—|\\+=}{{}}\n\t\r\f\v'
    delims = set()
    for ch in delimcharacters:
        delims.add(ch)
    #f = open(TextFilePath)

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

def compsaveWordFrequencies(tokenlist): #computes and saves word frequencies + longest length
    if(os.path.getsize('Logs/wordfreqs.log')==0):
        freq = dict()
    else:
        with open('Logs/wordfreqs.log', 'rb') as f:
            freq = pickle.load(f)

    if "most.tokens" in freq:
        freq['most.tokens'] = max(len(tokenlist), freq['most.tokens'])
    else:
        freq['most.tokens'] = len(tokenlist)

    for token in tokenlist:
        if token in freq:
            freq[token]+=1
        else:
            freq[token] = 1
    
    with open('Logs/wordfreqs.log', 'wb') as f:
        pickle.dump(freq, f)
    return freq

#takes in raw html and extracts the text, returning it in a string
def cleanHtml(rawtext):
    soup = BeautifulSoup(rawtext, "html.parser")
    cleanedtext = soup.get_text(separator=' ', strip=True)
    return cleanedtext

def clearLogs():
    open("Logs/wordfreqs.log", "w").close()

#TODO remove later
if __name__ == '__main__':
    file = open('utils/testhtml.txt') #test with string as well
    rawtext = file.read()
    cleantext = cleanHtml(rawtext)
    freq = compsaveWordFrequencies(tokenize(cleantext))
    print(freq)
    print("longest file so far:", freq['most.tokens'], "tokens")
    clearLogs() #clears the log

