
from nltk.parse.generate import generate, demo_grammar
from nltk import PCFG
import nltk
import re
from collections import defaultdict
import random
import bigrams
from random import choice

PUNCTUATION_LIST = ['.',',','?','!',"'",'"',':',';','-', ')', '(', '``', '\'\'']

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
    token = token.replace('\'s', ' is')
    if token == 'i' : #Upper case I is properly tagged, whereas lower case is not
        token = "I"
    return token

#Converted this to a list since it makes it easier later to check
#if a rule has already been added (and ignore it if so)
#Commenting out PCFG version for now in case we want it back

#"NP -> NNP" This rule is causing issues
#This list obviously can be modified

ruleList = \
["S -> NP VP",
"S -> NP VP PP",
"NP -> NP CC NP",
"NP -> PRP",
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

#Given a grammar, generate a random sample
def generate_sample(grammar, items):

    sample = ""
    for item in items: #All symbols to be parsed from a rule passed in
        if isinstance(item, nltk.Nonterminal):
            prodList = [prod.rhs() for prod in grammar.productions(lhs=item)]
            chosen_expansion = choice(prodList)
            sample += generate_sample(grammar, list(chosen_expansion))
        else:
            sample += str(item) + ' '
    return sample

def print_final_sentence(finalSentence) :
    finalString = ""
    for word in finalSentence :
        if word == 'BEGIN' :
            continue
        if isinstance(word, tuple) :
            word = word[0]
        finalString += word + ' '
    print finalString

def read_in_reviews(num_reviews, num_listings) :
    reviews = bigrams.parse_reviews('reviews.csv', num_reviews, num_listings)
    return reviews

def create_sentence_from_CFG(reviewSet, nplus, bigramDict) :

    for pair in nltk.pos_tag(reviewSet) : #Each pair should be (word, posTag)
        word, posTag = pair[0], pair[1]
        if posTag == "POS" or posTag in PUNCTUATION_LIST: #Hack for now
            continue
        second = stringModifications(posTag) #To get rid of "$" in PRP$
        if word == '\'in': #Not sure what this is, but let's ignore for now
            continue
        rule = second + " -> '" + tokenModifications(word) + "'"
        if rule in ruleList : #If we've already added this rule, don't duplicate
            continue
        ruleList.append(rule)

    grammarString = '\n'.join(ruleList)

    grammar = nltk.CFG.fromstring(grammarString)#, encoding="utf-8")

    #Generate a random sentence from our CFG
    sentence = generate_sample(grammar, [nltk.Nonterminal("S")])

    #Part of speech tag the resulting sentence
    posList = []
    for pair in nltk.pos_tag(sentence.split()) :
        posList.append(pair[1].replace('$', ''))

    #Slight hack, since formatting in bigrams is different based on value of nplus
    if nplus == 2 :
        currentWord = ('BEGIN',)
    else :
        currentWordList = [ ('BEGIN') for i in range(1, nplus)]
        currentWord = tuple(currentWordList)

    finalSentence = []
    for pos in posList :
        if currentWord in bigramDict.keys() and pos in bigramDict[currentWord].keys() :
            if nplus == 2 :
                currentWord = ((bigramDict[currentWord][pos]).keys()[0],)
            else : #Have to append everything in current word except for first element.
                listCur = list(currentWord)
                newList = listCur[1:]
                newList.append((bigramDict[currentWord][pos]).keys()[0])
                currentWord = tuple(newList)
        else : #No match in bigram dictionary TODO -> Add entry for this when we implement optimization
            if nplus == 2 :
                currentWord = (generate_sample(grammar, [nltk.Nonterminal(pos)]),)
            else :
                listCur = list(currentWord)
                newList = listCur[1:]
                newWord = (generate_sample(grammar, [nltk.Nonterminal(pos)]),)
                newList.append(newWord)
                currentWord = tuple(newList)

        finalSentence.append(currentWord[0])

    return finalSentence

if __name__ == '__main__':
    numReviews = 50
    nplus = 2
    numListings = 1
    listID = '1178162'
    reviews = read_in_reviews(numReviews, numListings)
    reviewSet = nltk.word_tokenize(''.join(reviews[listID]))
    bigramDict = bigrams.find_bigrams(reviews, nplus, listID)
    finalSentence = create_sentence_from_CFG(reviewSet, nplus, bigramDict)
    print_final_sentence(finalSentence)
    
