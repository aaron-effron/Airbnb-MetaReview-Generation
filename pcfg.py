###SC: general comments
###SC: Might be nice to have some more comments. Still not super sure what some
###     of this stuff does but from what I did understand it sems good
###SC: Also, is this eventually supposed to turn into our MDP? Because the last
###     part where you're actually generating random sentences seems to be 
###     sort of like the MDP, in which case we might want to start thinking
###     about explicitly formatting stuff to be "states", "actions", "transition
###     probability", and eventually "reward" when we get the correlation in.
###     And, we might want to split that part out so it's explicit what our
###     MDP is
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
###SC: moved to bigrams.py
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

'''
ruleList = \
["S -> NP VP [0.5]",
"S -> NP VP PP [0.5]",
"NP -> NNP [0.01]",
"NP -> NP CC NP [0.04]",
"NP -> PRP [0.1]",
"NP -> DT NN PP [0.1]",
"NP -> DT NNS PP [0.25]",
"NP -> DT NN [0.125]",
"NP -> DT JJ NN [0.125]",
"NP -> DT NNS [0.125]",
"NP -> DT JJ NNS [0.125]",
"VP -> VB [.125]",
"VP -> VBZ [.115]",
"VP -> VBD [.01]",
"VP -> VB NN [.25]",
"VP -> VB NP PP [0.5]",
"PP -> IN NP [1.0]"]
'''

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

def create_sentence_from_CFG(num_reviews, nplus) :

    #This later can be in some utility
    reviews = bigrams.parse_reviews('reviews.csv', num_reviews)
    text = nltk.word_tokenize(''.join(reviews['1178162']))

    counterDict = defaultdict(int)
    wordCounterDict = defaultdict(int)
    for pair in nltk.pos_tag(text) :
        wordCounterDict[pair[0]] += 1
        counterDict[stringModifications(pair[1])] += 1

    for pair in nltk.pos_tag(text) :
        if pair[1] == "POS" or pair[1] in PUNCTUATION_LIST: #Hack for now
            continue
        second = stringModifications(pair[1])
        if pair[0] == '\'in': #Not sure what this is, but let's ignore for now
            continue
        #rule = second + " -> '" + tokenModifications(pair[0]) + "'\t[" + str(float(1)/counterDict[second]) + "]"
        rule = second + " -> '" + tokenModifications(pair[0]) + "'"
        if rule in ruleList :
            continue
        ruleList.append(rule)

    grammarString = '\n'.join(ruleList)

    #grammar = nltk.PCFG.fromstring(grammarString)
    grammar = nltk.CFG.fromstring(grammarString)#, encoding="utf-8")
    viterbi_parser = nltk.ViterbiParser(grammar)

    #sentences = generate(grammar, n=NUM_SENTENCES, depth = 6)
    sentence = generate_sample(grammar, [nltk.Nonterminal("S")])

    ###SC: Just to make sure I understand, grammar is the random grammar
    ###     you generated, and posList is now the "empty" grammar we are going
    ###     to fill with our MDP?

    posList = []
    for pair in nltk.pos_tag(sentence.split()) :
        posList.append(pair[1].replace('$', ''))

    ###SC: I think my bigram dict matches up with how you generate your posList
    ###     However, one thing to consider when we have more time is that a lot
    ###     of these processes overlap (i.e. i do some of the same things in
    ###     bigrams). It's not an urgent fix and I think we should focus on 
    ###     getting something done for the report for now but it's something
    ###     to keep in mind for the future
    bigramDict = bigrams.find_bigrams(reviews, nplus)

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
            ###SC: not sure what this means?
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
    finalString = ""
    finalSentence = create_sentence_from_CFG(50, 3)
    for word in finalSentence :
        if word == 'BEGIN' :
            continue
        if isinstance(word, tuple) :
            word = word[0]
        finalString += word + ' '
    print finalString