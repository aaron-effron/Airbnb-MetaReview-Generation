from __future__ import division, unicode_literals
import csv
import nltk
from nltk.collocations import *
from nltk.corpus import wordnet as wn
from random import shuffle
from itertools import chain

######################################################################################

# Source: http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/

import math
from textblob import TextBlob as tb

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

######################################################################################

def find_sentence_with_word(word, reviews):
    for review in reviews:
        sentences = review.sentences
        for sentence in sentences:
            if word in sentence:
                return sentence

def get_listings_from_file():
  listings = {}

  with open('reviews.csv', 'rb') as csvfile:
      reader = csv.reader(csvfile)
      next(reader, None) # skip header
      for row in reader:
          listing_id = row[0]
          comments = tb(row[5].decode('unicode_escape').encode('ascii','ignore'))
          if listing_id not in listings:
              listings[listing_id] = [comments]
          else:
              listings[listing_id].append(comments)

  return listings
  
def get_most_significant_words(listings, listing_id):
    sorted_scores = []
    for i, review in enumerate(listings[listing_id]):
        scores = {word: tfidf(word, review, listings[listing_id]) for word in review.words}
        sorted_scores = sorted(scores.items()+sorted_scores, key=lambda x: x[1], reverse=True)
    
    return sorted_scores[:3]

def get_correlation_score(s1, listing1_keywords, s2, listing2_keywords):
    s1_lemmas = set([])
    s2_lemmas = set([])
    score = 0

    for keyword in listing1_keywords:
        if keyword in s1:
          synonyms = wn.synsets(keyword)
          s1_lemmas |= set(chain.from_iterable([word.lemma_names() for word in synonyms]))

    for keyword in listing2_keywords:
        if keyword in s2:
          synonyms = wn.synsets(keyword)
          s2_lemmas |= set(chain.from_iterable([word.lemma_names() for word in synonyms]))

    for s1_lemma in s1_lemmas:
      for s2_lemma in s2_lemmas:
        if s1_lemma == s2_lemma:
          score += 1 

    return score

listings = get_listings_from_file()
for i in range(len(listings.keys())-1):
    listing1 = listings.keys()[i]
    listing2 = listings.keys()[i+1]
    listing1_keywords = zip(*get_most_significant_words(listings, listing1))[0]
    listing2_keywords = zip(*get_most_significant_words(listings, listing2))[0]
    for s1 in listings[listing1]:
      for s2 in listings[listing2]:
        correlation_score = get_correlation_score(str(s1), listing1_keywords, str(s2), listing2_keywords) 
        if correlation_score > 0:
          print('Listing 1) %s' % (str(s1)))
          print('Listing 2) %s' % (str(s2)))
          print('Correlation score: %f' % (correlation_score))
          print('') 
