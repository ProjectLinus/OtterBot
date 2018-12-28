import nltk
import re
import sys
import math



stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', "that'll", 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

stopwords_pt = ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'ao', 'ele', 'das', 'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'você', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'numa', 'pelos', 'elas', 'qual', 'nós', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam','é']


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
                    invertedIndex[term].append([len(documentArray) - 1,50])
                else:
                    invertedIndex[term][-1][1] += 1
            else:
                invertedIndex[term] = [[len(documentArray) - 1,1]]
    return documentArray, invertedIndex


def createIndex(terms,docIndex,previousIndex):
    invertedIndex = previousIndex
    
    for term in terms:
        if(term in invertedIndex.keys()):
            if(invertedIndex[term][-1][0] != docIndex):
                invertedIndex[term].append([docIndex,1])
            else:
                invertedIndex[term][-1][1] += 1
        else:
            invertedIndex[term] = [[docIndex,1]]
    return invertedIndex






def cleanPhrase(phrase):
    phrase = re.sub(r'\W+',' ',phrase).lower()
    tokenlist = nltk.word_tokenize(phrase)
    filtered = []
    for token in tokenlist:
        if(token not in stopwords and token not in stopwords_pt):
            filtered.append(token)
    return filtered


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
        if(term in index.keys()):
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
