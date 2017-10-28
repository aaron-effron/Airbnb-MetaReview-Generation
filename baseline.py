from __future__ import division, unicode_literals
import csv
import nltk
from nltk.collocations import *
from random import shuffle

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

properties = {}

with open('reviews.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None) # skip header
    for row in reader:
        listing_id = row[0]
        comments = tb(row[5].decode('unicode_escape').encode('ascii','ignore'))
        if listing_id not in properties:
            properties[listing_id] = [comments]
        else:
            properties[listing_id].append(comments)

for listing_id in properties:
    if len(properties[listing_id]) < 5:
        continue
    sorted_scores = []
    for i, review in enumerate(properties[listing_id]):
        scores = {word: tfidf(word, review, properties[listing_id]) for word in review.words}
        sorted_scores = sorted(scores.items()+sorted_scores, key=lambda x: x[1], reverse=True)
       
   
    shuffle(properties[listing_id])
    sentences = []
    for item in sorted_scores[:3]:
        word, score = item
        sentences.append(find_sentence_with_word(word, properties[listing_id]))
    sentences = set(sentences)
    print listing_id, ': '
    for sentence in sentences:
        print sentence
    print ''