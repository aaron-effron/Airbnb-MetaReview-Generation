
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
NUM_ITERS = 50000

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
nplus = 3
numListings = 10
listingID = '1178162' 
reviews = { listingID : ["We had a wonderful time! The location is great! Sean's instructions and " 
                        "perfectly clear and communicating with him was easy. Getting the door unlocked "
                        "was a little tricky but once we figured it out, it was easy as can be. This was "
                        "our first trip to Boston and after exploring much of the city, we still decided this "
                        "would be a place we would stay again. Extremely close to Fenway and the Boston Back Bay"
                        "Area, everything was in walking distance or just a subway ride away. ",
                        "Sean, thanks for being such an awesome host for my boyfriend and I! The apartment was perfect "
                        "for our needs. We went to the game at Fenway and it was a very short walk to the festivities! "
                        "Bleacher bar before the game was a great spot! Great first time experience in Boston! We will "
                        "be returning :)",
                        "Sean was a good host and provided clear instructions on accessing his apartment. "
                        "The place was clean and comfortable.  The bed was super soft and cozy!  This place is "
                        "very convenient for getting around the city and is next to Fenway Park.  Thank you Sean "
                        "for having us.  I would stay here again if traveling through Boston."],
            '1234' : ["I would recommend staying with Lisa & Brian without any hesistation! The house is easy to get to, and the free transport passes (charliecards) were a huge help! Lisa was very accomodating, and easy to talk to. The house was lovely and some snacks were provided. This was my first experience of using AirBnB, and it by far exceeded my expectations!!"],
            '5678' : ["I have had a very good experience this time. "]}
fullBigramDict = bigrams.find_bigrams(reviews, 2, listingID) 
bigramDict = fullBigramDict if nplus == 2 else bigrams.find_bigrams(reviews, nplus, listingID)

#Given a grammar, generate a random sample
#positionList = []
def generate_sample(grammar, items, positionList):

    sample = ""

    for item in items: #All symbols to be parsed from a rule passed in
        if isinstance(item, nltk.Nonterminal):
            prodList = [prod.rhs() for prod in grammar.productions(lhs=item)]
                
            if not prodList :
                continue
                #return False #I don't know why this happens, but this fixes
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

def create_sentence_from_CFG(grammar, nplus, newWordWeight, explorationNum) :

    #Generate a random sentence from our CFG
    positionList = []
    sentence = generate_sample(grammar, [nltk.Nonterminal("S")], positionList)
    finalSentence = []

    #Slight hack, since formatting in bigrams is different based on value of nplus
    if nplus == 2 :
        currentWord = ('-BEGIN-',)
    else :
        currentWordList = [ ('-BEGIN-') for i in range(1, nplus)]
        currentWord = tuple(currentWordList)
        finalSentence.extend(currentWord)

    #finalSentence = [currentWord]

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
            # pos is in bigramDict keys, but hasn't been filled.  Honestly not sure if this is a bug,
            # so, keeping this print statement for now
            if not currWord : 
                print "We don't like when this happens!"
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
                #newList.append(weightedRandomChoice(bigramDict[currentWord][pos]))
                newList.append(currWord)
                currentWord = tuple(newList)
        elif not explore and nplus != 2 and \
        fullLookupKey in fullBigramDict.keys() and pos in fullBigramDict[fullLookupKey].keys() :
            # There's a match for the full dictionary, so let's add the word and add it to our
            # set
            newWord = weightedRandomChoice(fullBigramDict[fullLookupKey][pos])

            if currentWord not in bigramDict :
                bigramDict[currentWord] = {pos:{newWord: newWordWeight}}
            else:
                if pos not in bigramDict[currentWord]:
                    bigramDict[currentWord][pos] = {}
                bigramDict[currentWord][pos][newWord] = newWordWeight
            #[pos].append(newWord)
            listCur = list(currentWord)
            newList = listCur[1:]
            newList.append(newWord)
            currentWord = tuple(newList)

        else : 
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


            ### Just newly added
            if currWord not in bigramDict :
                bigramDict[currWord] = {pos:{newWord: .01}}
            else:
                if pos not in bigramDict[currWord]:
                    bigramDict[currWord][pos] = {}
                bigramDict[currWord][pos][newWord] = .01
            ###

        if (nplus != 2) :
            finalSentence.append(currentWord[-1])


        else :
            finalSentence.append(currentWord)

    return finalSentence, positionList

def runRLAlgorithm(grammar, listings, keywords, expNum, newWordWeight, rewardBoost, outputFile) :
    numReviews = len(listings[listingID])

    numChanges = 0
    bestCorrelation = 1 #To measure how many times correlation changes
    bestSentence = ''

    for i in range(0, NUM_ITERS) :
        '''
        if i > 0 and i % 1000 == 0 :
            outputFile.write("PARAMS iteration: {} rew:{} newW:{}, Num changes: {}, Best correlation: {}, best Sentence: {} \
                \n".format(i, rewardBoost, newWordWeight, numChanges, bestCorrelation, bestSentence))
            outputFile.flush()
        '''

        correlationScore = 0
        finalSentence, positionList = create_sentence_from_CFG(grammar, nplus, newWordWeight, expNum)
        
        #How to deal with error case when there is a word in bigram
        # But no matching POS tag 
        if len(finalSentence) == 0 and len(positionList) == 0: 
            continue

        finalSentenceString = final_sentence_as_string(finalSentence)
        #print "Final sentence in iteration {} is {}".format(i, finalSentenceString)
        for index, review in enumerate(listings[listingID]) :
            correlation_score, hits = synset.get_correlation_score(str(finalSentenceString), str(review), zip(*keywords)[0]) 
            correlationScore += correlation_score

        #Update weights
        avgCorrelation = float(correlationScore) / numReviews

        #print finalSentence

        key = [ ((finalSentence[idx])) for idx in range(0, min(nplus - 1, len(finalSentence)))]
        key = tuple(key)
        #print finalSentence
        #print key
        #print key in bigramDict.keys()
        #exit()
        for k in range(nplus - 1, len(finalSentence)) :
            #print finalSentence
            #print positionList
            word = finalSentence[k]
            pos = positionList[k - (nplus - 1)]
       
            if key in bigramDict.keys() and pos in bigramDict[key].keys() and word in bigramDict[key][pos].keys() :
                #print "Iteration {}, updating weight for key {}".format(i, key)
                #TODO: This can obviously be made more complex
                
                bigramDict[key][pos][word] += avgCorrelation + rewardBoost - 1 
                bigramDict[key][pos][word] = max(0.01, bigramDict[key][pos][word])
                
                '''
                if avgCorrelation > 1 :
                    bigramDict[key][pos][word] += 1
                else :
                    bigramDict[key][pos][word] -= 1
                    bigramDict[key][pos][word] = max(bigramDict[key][pos][word], 0.05)
                '''
                

            listCur = list(key)
            newList = listCur[1:]
            newList.append(word)
            key = tuple(newList)

        #for index, word in enumerate
        if avgCorrelation > bestCorrelation :
            outputFile.write("PARAMS iteration: {} rew:{} newW:{}, Num changes: {}, Best correlation: {}, best Sentence: {} \
                \n".format(i, rewardBoost, newWordWeight, numChanges, bestCorrelation, bestSentence))
            for k, v in bigramDict.items():
                outputFile.write(str(k) + ' >>> '+ str(v) + '\n')
            outputFile.flush()
            bestCorrelation = avgCorrelation
            bestSentence = final_sentence_as_string(finalSentence)
            numChanges += 1

    outputFile.write('\n\n\n\n')

    return numChanges, bestCorrelation, bestSentence

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

    with open('output_test_diffScore4.txt', 'a') as outputFile:
        #Could also tweak num reviews to compare to
        rewardList = [0.25]
        newWordWeightList = [0.5]
        print "BigramDict lengths: {}, {}".format(len(bigramDict.keys()), len(fullBigramDict.keys()))
        for rewardBoost in rewardList :
            for newWordWeight in newWordWeightList :
                expNum = 25
                print "RL time"
                numChanges, bestCorrelation, bestSentence = runRLAlgorithm(grammar, 
                    listings, keywords, expNum, newWordWeight, rewardBoost, outputFile)
                '''
                outputFile.write("PARAMS rew:{} newW:{}, Num changes: {}, Best correlation: {}, best Sentence: {} \
                \n".format(rewardBoost, newWordWeight, numChanges, bestCorrelation, bestSentence))
                '''
                outputFile.write("DONEZO TIME!!!")
                numChanges, bestCorrelation, bestSentence = runRLAlgorithm(grammar, 
                    listings, keywords, 0, newWordWeight, rewardBoost, outputFile)