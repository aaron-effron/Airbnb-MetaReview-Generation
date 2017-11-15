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
    
    return sorted_scores[:5]

def get_correlation_score(r1, r2, keywords):
    synsets = []
    score = 0
    hits = []

    for keyword in keywords:
        synonyms = wn.synsets(keyword)
        synsets.append((keyword, set(chain.from_iterable([word.lemma_names() for word in synonyms]))))

    for keyword, lemmas in synsets:
        if keyword in r1 and keyword in r2:
            hits.append(keyword)
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
                hits.append(synonym)
        if num_r1_hits > 0 and num_r2_hits > 0:
            score += num_r1_hits + num_r2_hits

    return score, hits

listings = get_listings_from_file()
keywords = get_most_significant_words(listings)
results = []
min_correlation_score = float('inf')
min_index = 0
count = 0
total = len(listings)
for listing_id in listings:
    if count == 300:
        break
    count += 1
    print('Processing listing %s (%d/%d)...' % (listing_id, count, total))
    if len(listings[listing_id]) < 5:
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
for i in range(10):
    listing_id, i, j, correlation_score, hits  = results[i]
    review1 = listings[listing_id][i]
    review2 = listings[listing_id][j]
    print('Review 1) %s' % (str(review1)))
    print('Review 2) %s' % (str(review2)))
    print('Correlation score: %f' % (correlation_score))
    print 'Keywords: ', hits
    print('') 
