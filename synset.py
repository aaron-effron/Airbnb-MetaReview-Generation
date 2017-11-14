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
          comments = tb(row[5].decode('unicode_escape').encode('ascii','ignore')).lower()
          if listing_id not in listings:
              listings[listing_id] = [comments]
          else:
              listings[listing_id].append(comments)

  return listings
  
def get_most_significant_words(listings):
    selected_reviews = None
    comparison_reviews = []
    comparison_review_count = 0

    for listing_id in listings:
        if comparison_review_count == 5:
            break
        if len(listings[listing_id]) > 5:
            if selected_reviews == None:
                selected_reviews = listings[listing_id]
            else:
                comparison_reviews += listings[listing_id]
                comparison_review_count += 1
  
    sorted_scores = []
    for i, review in enumerate(selected_reviews):
        scores = {word: tfidf(word, review, comparison_reviews) for word in review.words}
        sorted_scores = sorted(scores.items()+sorted_scores, key=lambda x: x[1], reverse=True)
    
    return sorted_scores[:10]

def get_correlation_score(s1, s2, keywords):
    lemmas = set([])
    score = 0

    for keyword in keywords:
        synonyms = wn.synsets(keyword)
        lemmas |= set(chain.from_iterable([word.lemma_names() for word in synonyms]))

    for lemma in lemmas:
        if lemma in s1 and lemma in s2:
            score += 1
    
    return score

listings = get_listings_from_file()
keywords = get_most_significant_words(listings)
for listing_id in listings:
    for i in range(len(listings[listing_id])-1):
        review1 = listings[listing_id][i]
        review2 = listings[listing_id][i+1]
        correlation_score = get_correlation_score(str(review1), str(review2), zip(*keywords)[0]) 
        if correlation_score > 0:
          print('Review 1) %s' % (str(review1)))
          print('Review 2) %s' % (str(review2)))
          print('Correlation score: %f' % (correlation_score))
          print('') 
