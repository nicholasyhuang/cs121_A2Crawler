#performs simhash on text, returns int simhash
def simhash(cleaned_text):
    SIMHASH_FINGERPRINT_SIZE = 64
    #quoting google "features are computed using standard IR techniques like tokenization, case folding, stop-word removal etc."
    #set of weighted featuers -> high dimensional vector, with 1 dimension per unique feature in all documents taken together
    #simhash can transform high dimensional vector into f-bit fingerprint where f is 64 bit
    #tokenize, then remove stopwords
    #take (weighted) features, hash each feature into 64 bits
    #features will "vote" and return 64 bits of a hash
    #hamming distances of 5-10 are good (start with 5)
    pass


def tokenize(TextFilePath):
    delimcharacters= ' ,.!?:;/—|\\+=}{{}}\n\t\r\f\v'
    delims = set()
    for ch in delimcharacters:
        delims.add(ch)
    f = open(TextFilePath)

    alphnum = set()
    alphanumeric = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'
    for ch in alphanumeric:
        alphnum.add(ch)
    
    token=''
    tokenlist = list()
    c = f.read(1)
    while(c!=''):
        if(c in delims and token!=''):
            tokenlist.append(token)
            token = ''
        elif c in alphnum: 
            token+=c.lower()

        c = f.read(1)
    if token!='':
        tokenlist.append(token)

    return tokenlist

def computeWordFrequencies(tokenlist):
    freq = dict()
    for token in tokenlist:
        if token in freq:
            freq[token]+=1
        else:
            freq[token] = 1
    return freq

