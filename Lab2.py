import nltk
import re
import sys
import math

def createIndexes(filename):
    documentArray = []
    invertedIndex = {}

    f = open(filename,'r',encoding='utf8')
    for doc in f:
        terms = cleanPhrase(doc)
        documentArray.append([doc,len(terms)])
        for term in terms:
            if(term in invertedIndex.keys()):
                if(invertedIndex[term][-1][0] != len(documentArray)-1):
                    invertedIndex[term].append([len(documentArray) - 1,1])
                else:
                    invertedIndex[term][-1][1] += 1
            else:
                invertedIndex[term] = [[len(documentArray) - 1,1]]
    return documentArray, invertedIndex


def createIndex(terms,numDocs):
    invertedIndex = {}
    
    for term in terms:
        if(term in invertedIndex.keys()):
            if(invertedIndex[term][-1][0] != numDocs-1):
                invertedIndex[term].append([numDocs - 1,1])
            else:
                invertedIndex[term][-1][1] += 1
        else:
            invertedIndex[term] = [[numDocs - 1,1]]
    return invertedIndex






def cleanPhrase(phrase):
    phrase = re.sub(r'\W+',' ',phrase).lower()
    return nltk.word_tokenize(phrase)


def printStatistics(documents,index):
    
    print('Total number of documents: ' + str(len(documents)))
    print('Total number of terms: ' + str(len(index.keys())))

    #what's the difference between terms and individual terms?


def printTermStats(termArray,documents,index):
    results = ''
    ndocs = len(documents)
    for term in termArray:
        if(term not in index.keys()):
            print('Term ' + term + ' is not present in any of the documents.')
        else:
            df = len(index[term])/ndocs
            arraytf = []
            for doc in index[term]:
                doctf = doc[1]/documents[doc[0]][1]
                arraytf.append(doctf)

            maxtf = max(arraytf)
            mintf = min(arraytf)
            idf = getInverseDocumentFrequency(documents,term,index[term])
            results += 'Stats for ' + term + ':\n'
            results += '- Document Frequency: ' + str(df) + "\n"
            results += '- Maximum Term Frequency: ' + str(maxtf) + "\n"
            results += '- Minimum Term Frequency: ' + str(mintf) + "\n"
            results += '- Inverse Document Frequency: ' + str(idf) + "\n"

    print(results)            

def getInverseDocumentFrequency(documents,term,invTermList):
    ndocs = len(documents)
    df = len(invTermList)/ndocs
    idf = math.log(ndocs/df)
    return(idf)
    


def prodSimilarity(termList,documents,index):
    pairList = {}
    for term in termList:
        if(term.lower() in index.keys()):
            inv = index[term]
            idf = getInverseDocumentFrequency(documents,term,index[term])
            for doc in inv:
                if(doc[0] not in pairList):
                    pairList[doc[0]] = 0
                pairList[doc[0]] += doc[1]/documents[doc[0]][1] * idf
    return pairList


def prodSimilarityOtter(termList,documents,index):
    pairList = {}
    for term in termList:
        if(term.lower() in index.keys()):
            inv = index[term]
            idf = getInverseDocumentFrequency(documents,term,index[term])
            for doc in inv:
                if(doc[0] not in pairList):
                    pairList[doc[0]] = 0
                pairList[doc[0]] += doc[1]/documents[doc[0]][2] * idf
    return pairList




def printProdSimil(pairList,documents):
    sortedPairs = sorted( ((v,k) for k,v in pairList.items()), reverse=True)
    for pair in sortedPairs:
        print(str(documents[pair[1]][0]) + str(pair[0]) + "\n")


def printQueryResponses(pairList,documents):
    sortedPairs = sorted( ((v,k) for k,v in pairList.items()), reverse=True)
    for pair in range(len(sortedPairs)):
        print(str(pair+1) + ': ' + str(documents[sortedPairs[pair][1]][0]))


def queryUser(documents,index):
    while(True):
        query = input("Please enter your query.\n")
        tokenizedQuery = cleanPhrase(query)
        similPairs = prodSimilarity(tokenizedQuery,documents,index)
        printQueryResponses(similPairs,documents)
