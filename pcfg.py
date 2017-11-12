
from nltk.parse.generate import generate, demo_grammar
from nltk import PCFG
import nltk
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
'''

sent = ['an', 'elephant', 'in', 'my', 'pajamas']
parser = nltk.ChartParser(groucho_grammar, nltk.parse.BU_STRATEGY)
trees = parser.nbest_parse(sent, trace=2)
