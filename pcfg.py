
from nltk.parse.generate import generate, demo_grammar
from nltk import PCFG
import nltk
import re
from collections import defaultdict
import random

PUNCTUATION_LIST = ['.',',','?','!',"'",'"',':',';','-', ')', '(', '``', '\'\'']
'''
grammar = nltk.PCFG.fromstring("""
    S    -> NP VP              [1.0]
    VP   -> TV NP              [0.4]
    VP   -> IV                 [0.3]
    VP   -> DatV NP NP         [0.3]
    TV   -> 'saw'              [1.0]
    IV   -> 'ate'              [1.0]
    DatV -> 'gave'             [1.0]
    NP   -> 'telescopes'       [0.001]
    NP   -> 'Jack'             [0.999]
    """)
viterbi_parser = nltk.ViterbiParser(grammar)

for sentence in generate(grammar, n=10):
    for tree in viterbi_parser.parse(sentence) :
        print tree

sent = ['an', 'elephant', 'in', 'my', 'pajamas']
parser = nltk.ChartParser(groucho_grammar, nltk.parse.BU_STRATEGY)
trees = parser.nbest_parse(sent, trace=2)
'''

review = '''My stay at islam's place was really cool! Good location, 
5min away from subway, then 10min from downtown. The room was nice, all place was clean. 
Islam managed pretty well our arrival, even if it was last minute ;) i do recommand this 
place to any airbnb user :)

We really enjoyed our stay at Islams house. From the outside the house didn't look so inviting 
but the inside was very nice! Even though Islam himself was not there everything was prepared 
for our arrival. The airport T Station is only a 5-10 min walk away. The only little issue was 
that all the people in the house had to share one bathroom. But it was not really a problem and 
it worked out fine. We would recommend Islams place for a stay in Boston. 

The place was really good, it is like 10 minutes from the airport so it was  
perfect for me because i had a connection flight, the taxi will cost u max 
15 dolars and if you go by shuttle is free, the house is very clean and the 
room was very confortable. The only thing is that i arrive and the owner wasnt 
there and i didnt read the instructions where he told me how to get in the house 
so i was waiting for about an hour, but if you read the instructions everything 
will be fine.

The host wasn't there, but it was fine. He left clear instructions, and we spent 
2 good nights there. It was a room was in a shared house, where there happened to 
be some interesting people staying, so we got to chat with some awesome people. The 
neighborhood is ok, had some good Colombian food.

Izzy was quick to reply to our request, and provided thorough instructions 
related to finding and entering the home. We loved the convenience of the 
location near the airport, as we weren't familiar with Boston, and landed 
late at night, so we didn't want to have to travel far or follow complicated directions 
to find the place. Although we never had any face-to-face contact with Izzy or anyone 
else in the home during our brief overnight stay, we felt comfortable there. 
Although we were assured that the neighborhood was safe, we were still feeling a 
bit on edge walking late at night from the Airport "T" station. Nonetheless, we 
made our way there without incident, and had a restful night of sleep before 
launching out the next day. Thanks, Izzy!

I didn't get a chance to meet Izzy but I thought the system that was set up was 
really well done. Things went quite smoothly upon arrival as per the detailed 
instructions that were left. 

We managed to get the key from the lock box easily which was nice because it provided 
flexibility for whatever time we arrived. This place is extremely close to the airport. 
I've never stayed next door to the airport before. Less than a 5 min ride to Airport 
Station which was then a 5 min walk.

Place had everything. Felt very homely like staying at a friends. Location was 
amazing!! East Boston has some hidden gem restaurants and proximity to Airport 
subway station was key. No complaints about the room or bathroom.

Great setup Izzy!
'''

text = nltk.word_tokenize(review)

def stringModifications(string) :
    string = string.replace('$', '')
    return string

def tokenModifications(token) :
    token = token.replace('n\'t', ' not')
    token = token.replace('\'ve', ' have')
    return token

string = """
S -> NP VP [1.0]\n
NP -> DT NN PP [0.5]\n
NP -> DT NN [0.5]\n
VP -> VB [.25]\n
VP -> VB NN [.25]\n
VP -> VB NP PP [0.5]\n
PP -> IN NP [1.0]\n
"""
counterDict = defaultdict(int)
for pair in nltk.pos_tag(text) :
    counterDict[stringModifications(pair[1])] += 1

for pair in nltk.pos_tag(text) :
    if pair[1] == "POS" or pair[1] in PUNCTUATION_LIST: #Hack for now
        continue
    second = stringModifications(pair[1])
    string += second + " -> '" + tokenModifications(pair[0]) + "'\t[" + str(float(1)/counterDict[second]) + "]\n"

#print string
grammar = nltk.PCFG.fromstring(string)
viterbi_parser = nltk.ViterbiParser(grammar)

NUM_SENTENCES = 5000

sentences = generate(grammar, n=NUM_SENTENCES, depth = 6)
sentenceList = list(sentences)

for i in range(0, 10) :
    rand = random.randint(0, NUM_SENTENCES)
    sentence = sentenceList[rand]
    print rand, sentence
    #for tree in viterbi_parser.parse(sentence) :
    #    print tree