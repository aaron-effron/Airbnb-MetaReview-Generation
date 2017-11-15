from __future__ import division, unicode_literals
import csv
import nltk
from nltk.collocations import *
from nltk.corpus import wordnet as wn
from random import shuffle
from itertools import chain
from random import shuffle, randint

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

NUM_COMPARISON_REVIEWS = 5
MIN_REVIEW_COUNT = 5
MAX_SAMPLE_LISTINGS = 300
MAX_SAMPLE_RESULTS = 10

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
  
def get_most_significant_words(listings, listing_id):    
    selected_reviews = listings[listing_id]
    comparison_reviews = []
    comparison_review_count = 0

    listing_ids = listings.keys()
    shuffle(listing_ids)

    for listing_id in listing_ids:
        if comparison_review_count == NUM_COMPARISON_REVIEWS:
            break
        if len(listings[listing_id]) > MIN_REVIEW_COUNT:
            comparison_reviews += listings[listing_id]
            comparison_review_count += 1
  
    sorted_scores = []
    for i, review in enumerate(selected_reviews):
        scores = {word: tfidf(word, review, comparison_reviews) for word in review.words}
        sorted_scores = sorted(scores.items()+sorted_scores, key=lambda x: x[1], reverse=True)
    
    return sorted_scores[:5]

def get_correlation_score(r1, r2, keywords):
    synsets = []
    score = 0
    hits = set([])

    for keyword in keywords:
        synonyms = wn.synsets(keyword)
        synsets.append((keyword, set(chain.from_iterable([word.lemma_names() for word in synonyms]))))

    for keyword, lemmas in synsets:
        if keyword in r1 and keyword in r2:
            hits.add(keyword)
            score += 2
        num_r1_hits = 0
        num_r2_hits = 0
        for synonym in lemmas:
            syn_count = 0
            if synonym in r1:
                num_r1_hits += 1
                syn_count += 1
            if synonym in r2:
                num_r2_hits += 1
                syn_count += 1
            if syn_count > 0:
                hits.add(synonym)
        if num_r1_hits > 0 and num_r2_hits > 0:
            score += num_r1_hits + num_r2_hits

    return score, hits

# Sample usage:
listings = get_listings_from_file()
random_id = listings.keys()[randint(0, len(listings.keys())-1)]
keywords = get_most_significant_words(listings, random_id)
results = []
count = 0
total = len(listings)
for listing_id in listings:
    if count == MAX_SAMPLE_LISTINGS:
        break
    count += 1
    print('Processing listing %s (%d/%d)...' % (listing_id, count, MAX_SAMPLE_LISTINGS))
    if len(listings[listing_id]) < MIN_REVIEW_COUNT:
        continue
    for i in range(len(listings[listing_id])):
        for j in range(len(listings[listing_id])):
            if i == j:
                continue
            review1 = listings[listing_id][i]
            review2 = listings[listing_id][j]
            correlation_score, hits = get_correlation_score(str(review1), str(review2), zip(*keywords)[0]) 
            results.append((listing_id, i, j, correlation_score, hits))
results.sort(key = lambda r: r[3], reverse=True)
for i in range(MAX_SAMPLE_RESULTS):
    listing_id, i, j, correlation_score, hits  = results[i]
    review1 = listings[listing_id][i]
    review2 = listings[listing_id][j]
    print('Review 1) %s' % (str(review1)))
    print('Review 2) %s' % (str(review2)))
    print('Correlation score: %f' % (correlation_score))
    print 'Keywords: ', hits
    print('') 
