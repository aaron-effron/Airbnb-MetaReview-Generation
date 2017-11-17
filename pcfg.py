
from nltk.parse.generate import generate, demo_grammar
from nltk import PCFG
import nltk
import re
from collections import defaultdict
import random
import bigrams
import synset
import parsing
from random import choice

PUNCTUATION_LIST = ['.',',','?','$','!',"'",'"',':',';','-', ')', '(', '``', '\'\'']

#Borrowed from Car Assignment
# Function: Weighted Random Choice
# --------------------------------
# Given a dictionary of the form element -> weight, selects an element
# randomly based on distribution proportional to the weights. Weights can sum
# up to be more than 1. 
def weightedRandomChoice(weightDict):
    weights = []
    elems = []
    for elem in weightDict:
        weights.append(weightDict[elem])
        elems.append(elem)
    total = sum(weights)
    key = random.uniform(0, total)
    runningTotal = 0.0
    chosenIndex = None
    for i in range(len(weights)):
        weight = weights[i]
        runningTotal += weight
        if runningTotal > key:
            chosenIndex = i
            return elems[chosenIndex]
    raise Exception('Should not reach here')


#Modification for "PRP$" to not have dollar sign
def stringModifications(string) :
    string = string.replace('$', '')
    return string

#Function to deal with contractions as well as lower case i
#NOTE: As written, we still need this, because bigrams.py doesn't do this
#in file input. 
def tokenModifications(token) :
    token = token.replace('n\'t', ' not')
    token = token.replace('\'ve', ' have')
    token = token.replace('\'ll', ' will')
    token = token.replace('\'d', ' would')
    token = token.replace('\'re', ' are')
    token = token.replace('\'s', ' is')
    token = token.replace('\'m', ' am')
    token = token.replace('airbnb\'ers', 'airbnbers')
    if token == 'i' : #Upper case I is properly tagged, whereas lower case is not
        token = "I"
    return token

#This non-terminal section can obviously be appended to

ruleList = \
["S -> NP VP",
"S -> NP VP PP",
"NP -> NP CC NP",
"NP -> PRP NN",
"NP -> DT NN PP",
"NP -> DT NNS PP",
"NP -> DT NN",
"NP -> DT JJ NN",
"NP -> DT NNS",
"NP -> DT JJ NNS",
"VP -> VB",
"VP -> VBZ",
"VP -> VBD",
"VP -> VB NN",
"VP -> VB NP PP",
"PP -> IN DT NP"]

#Trying to make the CFG more diverse
ruleList.append("VP -> VBD RB JJ")
ruleList.append("VP -> VBD JJ")
ruleList.append("NP -> JJ NNS")
ruleList.append("NP -> CD NNS")
ruleList.append("NP -> NP IN PP")
ruleList.append("S -> NP CC NP")
ruleList.append("VP -> VP TO VP")
ruleList.append("VP -> VP TO NP")
#ruleList.append("NP -> NNP") #I'd like to include this rule, but it's not helping

numReviews = 100
nplus = 3
numListings = 10
listingID = '1178162'
reviews = parsing.parse_reviews('reviews.csv', numReviews, numListings)
fullBigramDict = bigrams.find_bigrams(reviews, 2, listingID) 
bigramDict = fullBigramDict if nplus == 2 else bigrams.find_bigrams(reviews, nplus, listingID)

#Given a grammar, generate a random sample
def generate_sample(grammar, items):

    sample = ""
    for item in items: #All symbols to be parsed from a rule passed in
        if isinstance(item, nltk.Nonterminal):
            prodList = [prod.rhs() for prod in grammar.productions(lhs=item)]
            if not prodList :
                continue
                #return False #I don't know why this happens, but this fixes
            chosen_expansion = choice(prodList)
            sample += generate_sample(grammar, list(chosen_expansion))
        else:
            sample += str(item) + ' '
    return sample

def final_sentence_as_string(finalSentence) :
    finalString = ""
    for word in finalSentence :
        if word == '-BEGIN-' :
            continue
        if isinstance(word, tuple) :
            word = word[0]
        finalString += word + ' '
    return finalString

def create_CFG_from_reviews(reviewSet) : #Appending to non-terminal rules defined globally

    for pair in nltk.pos_tag(reviewSet) : #Each pair should be (word, posTag)
        word, posTag = pair[0], pair[1]
        if posTag == "POS" or posTag in PUNCTUATION_LIST: #Hack for now
            continue
        second = stringModifications(posTag) #To get rid of "$" in PRP$
        if word == '\'in':# or word == '\'m': #Not sure what this is, but let's ignore for now
            continue
        rule = second + " -> '" + tokenModifications(word) + "'"
        if rule in ruleList : #If we've already added this rule, don't duplicate
            continue
        ruleList.append(rule)

    grammarString = '\n'.join(ruleList)

    grammar = nltk.CFG.fromstring(grammarString)

    return grammar

def create_sentence_from_CFG(grammar, nplus, bigramDict, fullBigramDict) :

    #Generate a random sentence from our CFG
    sentence = generate_sample(grammar, [nltk.Nonterminal("S")])

    #Part of speech tag the resulting sentence
    posList = []
    for pair in nltk.pos_tag(sentence.split()) :
        posList.append(pair[1].replace('$', ''))

    #Slight hack, since formatting in bigrams is different based on value of nplus
    if nplus == 2 :
        currentWord = ('-BEGIN-',)
    else :
        currentWordList = [ ('-BEGIN-') for i in range(1, nplus)]
        currentWord = tuple(currentWordList)

    finalSentence = []
    for pos in posList :

        #If nplus > 2, this is the key we'll lookup for the full dictionary if there's 
        # no match in the specific dictionary
        fullLookupKey = (currentWord[-1],)
    
        #If there is a bigram for the current transition we are considering, follow that
        if currentWord in bigramDict.keys() and pos in bigramDict[currentWord].keys() :
            if nplus == 2 :
                #Make a choice weighted by the bigram probabilities
                currentWord = (weightedRandomChoice(bigramDict[currentWord][pos]),)
            else : 
                #Append the new word to everything in the current word except for first element.
                #For example, ("boy in the", "park") should become ("in the park")
                #Doing list and tuple conversion because lists are mutable, whereas tuples are 
                #the actual form we want in our dictionary
                listCur = list(currentWord)
                newList = listCur[1:]
                newList.append(weightedRandomChoice(bigramDict[currentWord][pos]))
                currentWord = tuple(newList)
        elif nplus != 2 and \
        fullLookupKey in fullBigramDict.keys() and pos in fullBigramDict[fullLookupKey].keys() :
            # There's a match for the full dictionary, so let's add the word and add it to our
            # set
            newWord = weightedRandomChoice(fullBigramDict[fullLookupKey][pos])

            if currentWord not in bigramDict :
                bigramDict[currentWord] = {pos:{newWord: 0.5}}
            else:
                if pos not in bigramDict[currentWord]:
                    bigramDict[currentWord][pos] = {}
                bigramDict[currentWord][pos][newWord] = 0.5
            #[pos].append(newWord)
            listCur = list(currentWord)
            newList = listCur[1:]
            newList.append(newWord)
            currentWord = tuple(newList)

        else : 
            #No match in bigram dictionary, choose a random word 
            #TODO -> Add entry for this when we implement optimization
            if nplus == 2 :
                #[:-1] since last word has a space after it
                currentWord = (generate_sample(grammar, [nltk.Nonterminal(pos)])[:-1],)
            else : #See above for logic here
                listCur = list(currentWord)
                newList = listCur[1:]

                #[:-1] since last word has a space after it
                newWord = (generate_sample(grammar, [nltk.Nonterminal(pos)])[:-1]) 
                newList.append(newWord)
                currentWord = tuple(newList)

        finalSentence.append(currentWord[-1])

    return finalSentence, posList

if __name__ == '__main__':
    reviewSet = []
    for review in reviews[listingID]:
        sents = parsing.parse_sentences(review)
        for sent in sents:
            reviewSet += sent
    grammar = create_CFG_from_reviews(reviewSet)
    
    listings = synset.convert_review_to_text_blobs(reviews)

    #Correlation score

    keywords = synset.get_most_significant_words(reviews, listingID)

    numReviews = len(listings[listingID])

    NUM_ITERS = 10000
    for i in range(0, NUM_ITERS) :
        correlationScore = 0
        finalSentence, posList = create_sentence_from_CFG(grammar, nplus, bigramDict, fullBigramDict)
        
        finalSentenceString = final_sentence_as_string(finalSentence)

        for index, review in enumerate(listings[listingID]) :
            correlation_score, hits = synset.get_correlation_score(str(finalSentenceString), str(review), zip(*keywords)[0]) 
            correlationScore += correlation_score

        #Update weights
        avgCorrelation = float(correlationScore) / numReviews

        key = [ ((finalSentence[i])) for i in range(0, nplus - 1)]
        key = tuple(key)
        for k in range(nplus - 1, len(finalSentence)) :
            word = finalSentence[k]
            pos = posList[k - (nplus - 2)]
            
            #Part of speech tagging is annoyingly sentence dependent, and thus we need this separation
            #TODO : Fix this hack to deal with random cases
            if key in bigramDict.keys() and pos in bigramDict[key].keys() and word in bigramDict[key][pos].keys() :
                #TODO: This can obviously be made more complex
                if avgCorrelation > 0.7 :
                    bigramDict[key][pos][word] *= 1.1
                else :
                    bigramDict[key][pos][word] *= .9

            listCur = list(key)
            newList = listCur[1:]
            newList.append(word)
            key = tuple(newList)

        #for index, word in enumerate
        if avgCorrelation > 1 :
            print "Average correlation for {} is {}".format(finalSentenceString, float(correlationScore) / numReviews)

    #print_final_sentence(finalSentence)
    
