import re
from bs4 import BeautifulSoup
import pickle
import os
from hashlib import md5

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

def updateMostTokens(tokenlist):

    with open('Logs/wordfreqs.log', 'rb') as f:
        if(os.path.getsize('Logs/wordfreqs.log')==0):
            freq = dict()
        else:
            freq = pickle.load(f)
        f.close()

    if "most.tokens" in freq:
        freq['most.tokens'] = max(len(tokenlist), freq['most.tokens'])
    else:
        freq['most.tokens'] = len(tokenlist)
    
    with open('Logs/wordfreqs.log', 'wb') as f:
        pickle.dump(freq, f)
        f.close()

def compsaveWordFrequencies(tokenlist): #computes and saves word frequencies
    if(os.path.getsize('Logs/wordfreqs.log')==0):
        freq = dict()
    else:
        with open('Logs/wordfreqs.log', 'rb') as f:
            freq = pickle.load(f)
            f.close()

    #most.tokens shouldb e moved to separate function

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

def clearLogs():
    open("Logs/wordfreqs.log", "w").close()

#TODO remove later
if __name__ == '__main__':
    file1 = open('utils/testhtml.txt')
    file2 = open('utils/testhtml copy.txt')
    file3 = open('utils/testhtml2.txt')
    tokens1 = cleanStopwords(tokenize(cleanHtml(file1.read())))
    tokens2 = cleanStopwords(tokenize(cleanHtml(file2.read())))
    tokens3 = cleanStopwords(tokenize(cleanHtml(file3.read())))
    updateMostTokens(tokens1)
    print(compsaveWordFrequencies(tokens1))
    clearLogs()
    #print(cleanStopwords(tokens))
    h1 = simhash(tokens1)
    h2 = simhash(tokens2)
    h3 = simhash(tokens3)

    print(h1)
    print(h2)
    print(h3)
    if(similarHashes(h1, h2)):
        print("YES doc1 doc2 SIMILAR (expected)")
    else:
        print("NO doc1 doc2 ARE NOT SIMILAR (shit)")

    if(similarHashes(h1, h3)):
        print("YES doc1 doc3 ARE SIMILAR (shit)")
    else:
        print("NO doc1 doc3 ARE NOT SIMILAR (expected)")
    