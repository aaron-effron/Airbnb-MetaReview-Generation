
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
from numpy import exp
import matplotlib.pyplot as plt
import numpy as np
import Queue

PUNCTUATION_LIST = ['.',',','?','$','!',"'",'"',':',';','-', ')', '(', '``', '\'\'']
NUM_ITERS = 100000
CORRELATION_WEIGHT = .7
LENGTH_WEIGHT = 1 - CORRELATION_WEIGHT
OPTIMAL_SENTENCE_LENGTH = 10

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

    return False

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
"PP -> IN NP"]

#Trying to make the CFG more diverse

ruleList.append("VP -> VBD RB JJ")
ruleList.append("VP -> VBD JJ")
ruleList.append("NP -> JJ NNS")
ruleList.append("NP -> CD NNS")
ruleList.append("NP -> NP IN PP")
ruleList.append("VP -> VP TO VP")
ruleList.append("VP -> VP TO NP")

#ruleList.append("NP -> NNP") #I'd like to include this rule, but it's not helping

numReviews = 100
nplus = 5
numListings = 10
listingID = '447826'
reviews = parsing.parse_reviews('reviews.csv', numReviews, numListings, listingID)

fullBigramDict, fullGrammarDict = bigrams.find_bigrams(reviews, 2, listingID)
if nplus == 2:
    bigramDict = fullBigramDict
    grammarDict = fullGrammarDict  
else:
    bigramDict, grammarDict = bigrams.find_bigrams(reviews, nplus, listingID)

#Given a grammar, generate a random sample
def generate_sample(grammar, items, positionList):

    sample = ""

    for item in items: #All symbols to be parsed from a rule passed in
        if isinstance(item, nltk.Nonterminal):
            prodList = [prod.rhs() for prod in grammar.productions(lhs=item)]

            if not prodList :
                continue
            chosen_expansion = choice(prodList)

            if len(chosen_expansion) == 1 and not isinstance(chosen_expansion[0], nltk.Nonterminal) :
                positionList.append(str(item).replace('$', ''))

            sample += generate_sample(grammar, list(chosen_expansion), positionList)
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

def generate_base_grammar_set(nplus) :

    currentWord = 'BEGIN'
    posList = []
    grammarSet = [ ('-BEGIN-') for i in range(0, nplus - 1)]
    while currentWord[-1] != "." :
        grammarTup = tuple(grammarSet)
        fullLookupKey = (grammarTup)
        nextPos = random.choice(grammarDict[fullLookupKey])
        posList.append(nextPos)

        #[pos].append(newWord)
        listCur = list(grammarTup)
        newList = listCur[1:]
        newList.append(nextPos)
        currentWord = tuple(newList)
        grammarSet = newList
    return posList

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

def create_sentence_from_grammarDict(positionList, nplus) :

    finalSentence = []
    currentWordList = [ ('-BEGIN-') for i in range(0, nplus - 1)]
    currentWord = tuple(currentWordList)
    endSentence = False
    for pos in positionList :

        #If nplus > 2, this is the key we'll lookup for the full dictionary if there's
        # no match in the specific dictionary

        #If there is a bigram for the current transition we are considering, follow that
        if currentWord in bigramDict.keys() and pos in bigramDict[currentWord].keys() :
            currWord = weightedRandomChoice(bigramDict[currentWord][pos])

            # This is very uncommon, but need to have so we don't crash.  Essentially, this means that
            # pos is in bigramDict keys, but hasn't been filled.  Honestly not sure if this is a bug,
            # so, keeping this print statement for now
            if not currWord :
                print "THIS SHOULD NOT HAPPEN!"
                return [], []
            if nplus == 2 :
                #Make a choice weighted by the bigram probabilities
                #currentWord = (weightedRandomChoice(bigramDict[currentWord][pos]),)
                currentWord = (currWord,)
            else :
                #Append the new word to everything in the current word except for first element.
                #For example, ("boy in the", "park") should become ("in the park")
                #Doing list and tuple conversion because lists are mutable, whereas tuples are
                #the actual form we want in our dictionary
                listCur = list(currentWord)
                newList = listCur[1:]
                newList.append(currWord)
                currentWord = tuple(newList)

            if (nplus != 2) :
                finalSentence.append(currentWord[-1])
            else :
                finalSentence.append(currentWord)

        else: #This is the end of the sentence
            if endSentence :
                return []
            endSentence = True

    return finalSentence

def create_sentence_from_CFG(grammar, nplus, explorationNum) :

    #Generate a random sentence from our CFG
    positionList = []
    sentence = generate_sample(grammar, [nltk.Nonterminal("S")], positionList)

    finalSentence = []

    #Formatting in bigrams is different based on value of nplus
    if nplus == 2 :
        currentWord = ('-BEGIN-',)
    else :
        currentWordList = [ ('-BEGIN-') for i in range(1, nplus)]
        currentWord = tuple(currentWordList)
        finalSentence.extend(currentWord)


    # Don't want position list that we return to change anymore, but need
    # to pass one in for generate_sample to work.
    dummyPosList = []
    for pos in positionList :

        #If nplus > 2, this is the key we'll lookup for the full dictionary if there's
        # no match in the specific dictionary
        fullLookupKey = (currentWord[-1],)

        explore = False if random.randint(1, 100) > explorationNum else True

        #If there is a bigram for the current transition we are considering, follow that

        if not explore and currentWord in bigramDict.keys() and pos in bigramDict[currentWord].keys() :
            currWord = weightedRandomChoice(bigramDict[currentWord][pos])

            # This is very uncommon, but need to have so we don't crash.  Essentially, this means that
            # pos is in bigramDict keys, but hasn't been filled. 
            if not currWord :
                return [], []
            if nplus == 2 :
                #Make a choice weighted by the bigram probabilities
                #currentWord = (weightedRandomChoice(bigramDict[currentWord][pos]),)
                currentWord = (currWord,)
            else :
                #Append the new word to everything in the current word except for first element.
                #For example, ("boy in the", "park") should become ("in the park")
                #Doing list and tuple conversion because lists are mutable, whereas tuples are
                #the actual form we want in our dictionary
                listCur = list(currentWord)
                newList = listCur[1:]
                newList.append(currWord)
                currentWord = tuple(newList)
        elif not explore and nplus != 2 and \
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
            listCur = list(currentWord)
            newList = listCur[1:]
            newList.append(newWord)
            currentWord = tuple(newList)

        else : 
            if explorationNum == 0:
                break
            #No match in bigram dictionary (or explore), choose a random word 
            currWord = currentWord

            if nplus == 2 :
                #[:-1] since last word has a space after it
                currentWord = (generate_sample(grammar, [nltk.Nonterminal(pos), dummyPosList])[:-1])
            else : #See above for logic here
                listCur = list(currentWord)
                newList = listCur[1:]

                #[:-1] since last word has a space after it
                newWord = (generate_sample(grammar, [nltk.Nonterminal(pos)], dummyPosList)[:-1])
                newList.append(newWord)
                currentWord = tuple(newList)

            if currWord not in bigramDict :
                bigramDict[currWord] = {pos:{newWord: .01}}
            else:
                if pos not in bigramDict[currWord]:
                    bigramDict[currWord][pos] = {}
                bigramDict[currWord][pos][newWord] = .01

        if (nplus != 2) :
            finalSentence.append(currentWord[-1])
        else :
            finalSentence.append(currentWord)

    return finalSentence, positionList

def runRLAlgorithm(grammar, listings, keywords, expNum, outputFile) :
    numReviews = len(listings[listingID])

    numChanges = 0
    bestScore = 0.0 #To measure how many times correlation changes
    bestSentence = ''
    bestOverTime = []
    OverTime = []
    top10 = Queue.PriorityQueue(maxsize=10)
    lowestScore = 0.0
    sentences_seen = []

    for i in range(0, NUM_ITERS) :
        correlationScore = 0

        positionList = generate_base_grammar_set(nplus)
        finalSentence = create_sentence_from_grammarDict(positionList, nplus)

        #Old implementation, using CFG
        #finalSentence, positionList = create_sentence_from_CFG(grammar, nplus, expNum)

        # How to deal with error case when there is a word in bigram
        # But no matching POS tag
        if len(finalSentence) == 0 or len(positionList) == 0:
            # Our sentence did not complete, so the best score remains the same
            # and the actual score is a 0 (no sentence = score of 0)
            bestOverTime.append(bestScore)
            OverTime.append(0)
            continue
        #TODO: Should probably use this
        '''  
        if len(finalSentence) - nplus + 1 < len(positionList): #Whole sentence couldn't be filled
            continue
        '''

        finalSentenceString = final_sentence_as_string(finalSentence)
        for index, review in enumerate(listings[listingID]) :
            correlation_score, hits = synset.get_correlation_score(str(finalSentenceString), str(review), zip(*keywords)[0])
            correlationScore += correlation_score

        #Update weights
        avgCorrelation = float(correlationScore) / numReviews

        #Old code for CFG
        #key = [ ((finalSentence[idx])) for idx in range(0, min(nplus - 1, len(finalSentence)))]
        #key = tuple(key)

        def sigmoid(x):
            return 1.0 / (1 + exp(-x))

        updatedScore = sigmoid(CORRELATION_WEIGHT*avgCorrelation - LENGTH_WEIGHT*(min((len(finalSentence) - OPTIMAL_SENTENCE_LENGTH)**2, 400)))

        grammarSet = [ ('-BEGIN-') for i in range(0, nplus - 1)]
        currentWord = tuple(grammarSet)
        for il in range(0, len(finalSentence)) :
            pos = positionList[il]
            word = finalSentence[il]
            key = currentWord

            if key in bigramDict.keys() and pos in bigramDict[key].keys() and word in bigramDict[key][pos].keys() :

                bigramDict[key][pos][word] += updatedScore
                bigramDict[key][pos][word] = max(0.01, bigramDict[key][pos][word])

            listCur = list(currentWord)
            newList = listCur[1:]
            newList.append(word)
            currentWord = tuple(newList)

        '''
        for k in range(nplus - 1, len(finalSentence)) :
            word = finalSentence[k]
            pos = positionList[k - (nplus - 1)]

            if key in bigramDict.keys() and pos in bigramDict[key].keys() and word in bigramDict[key][pos].keys() :
                print "WE IN HERE!"
                #TODO: This can obviously be made more complex

                bigramDict[key][pos][word] += 3*avgCorrelation - 1

                bigramDict[key][pos][word] = max(0.01, bigramDict[key][pos][word])


            listCur = list(key)
            newList = listCur[1:]
            newList.append(word)
            key = tuple(newList)
        '''

        if updatedScore > lowestScore:
            to_add = final_sentence_as_string(finalSentence)
            if to_add not in sentences_seen:
                # Make room for the new sentence
                if top10.full():
                    # Remove lowest scoring sentence from queue
                    removed = top10.get()
                    assert removed[0] <= updatedScore, "Removed sentence's score is better than the score of the sentence added"
                    # Python's queue has no peek() function, so to simulate peek
                    # we remove the next lowest scoring sentence, save that
                    # score as the threshold score, then put the sentence back
                    # in the queue
                    getLowScore = top10.get()
                    lowestScore = getLowScore[0]
                    #print "lowest score now ", lowestScore
                    top10.put(getLowScore)
                top10.put((updatedScore, to_add))
                sentences_seen.append(to_add)
            
        if updatedScore > bestScore :
            bestScore = updatedScore
            bestSentence = final_sentence_as_string(finalSentence)
            outputFile.write("PARAMS iteration: {}, Num changes: {}, Best correlation: {}, best Sentence: {} \
                \n".format(i, numChanges, bestScore, bestSentence))
            outputFile.flush()
            numChanges += 1
        bestOverTime.append(bestScore)
        OverTime.append(updatedScore)

    if expNum == 0:
        plt.figure()
        plt.scatter(range(1, NUM_ITERS+1), bestOverTime, s=3)
        plt.title("Best Correlation Scores (Cumulative)")
        plt.xlabel("Iteration Number")
        plt.ylabel("Best Correlation Score")
        plt.savefig('iterVSbest'+str(nplus-1)+'gram.png')

        plt.figure()
        plt.scatter(range(1, NUM_ITERS+1), OverTime, s=3)
        plt.title("Correlation Scores from Each Iteration")
        plt.xlabel("Iteration Number")
        plt.ylabel("Correlation Score")
        plt.savefig('iterVSscore'+str(nplus-1)+'.png')

    return numChanges, bestScore, bestSentence, top10

if __name__ == '__main__':
    reviewSet = []
    for review in reviews[listingID]:
        sents = parsing.parse_sentences(review)
        for sent in sents:
            reviewSet += sent
    #grammar = create_CFG_from_reviews(reviewSet)
    grammar = {} #Isn't used, so just initialize to dictionary

    listings = synset.convert_review_to_text_blobs(reviews)

    #Correlation score

    keywords = synset.get_most_significant_words(reviews, listingID)

    with open('output.txt', 'a') as outputFile:
        #Could also tweak num reviews to compare to
        outputFile.write("\n\n\n\n")
        outputFile.write("Using nplus="+str(nplus)+"\n")

        np.seterr(all='raise')
        expNum = 0
        
        numChanges, bestScore, bestSentence, top10 = runRLAlgorithm(grammar,
            listings, keywords, expNum, outputFile)
        while not top10.empty():
            sent = top10.get()
            print "Score of ", sent[0], " sentence is ", sent[1]
            outputFile.write("Score: "+str(sent[0])+"\n")
            outputFile.write(sent[1]+"\n")
        outputFile.write("Now testing with optimized parameters")
        numChanges, bestScore, bestSentence, top10 = runRLAlgorithm(grammar,
            listings, keywords, 0, outputFile)
        while not top10.empty():
            sent = top10.get()
            print "Score of ", sent[0], " sentence is ", sent[1]
            outputFile.write("Score: "+str(sent[0])+"\n")
            outputFile.write(sent[1]+"\n")
        print("Best score is: ", bestScore)
        print("Best sentence is: ", bestSentence)
