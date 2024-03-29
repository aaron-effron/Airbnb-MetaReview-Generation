from __future__ import division, unicode_literals
import csv
import nltk
from nltk.collocations import *
from nltk.corpus import wordnet as wn
from random import shuffle
from itertools import chain
from random import shuffle, randint
import parsing

######################################################################################

# Source: http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/
# Calculating TF-IDF

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

NUM_COMPARISON_REVIEWS = 20
MIN_REVIEW_COUNT = 5
MAX_SAMPLE_LISTINGS = 300
MAX_SAMPLE_RESULTS = 10
NUM_TF_IDF_ITERATIONS = 10
MAX_COMPARISONS_PER_LISTING = 20

# Text blobs are used in TF-IDF, so we need to convert
def convert_review_to_text_blobs(reviews):
    listings = {}
    for listID in reviews:
        listings[listID] = []
        for review in reviews[listID]:
            new_rev = ''
            sentences = parsing.parse_sentences(review)
            for sent in sentences:
                #print "Sentence: ", sent
                sent = ' '.join(sent)
                if new_rev != '':
                    new_rev += '. '
                new_rev += sent
            listings[listID].append(tb(new_rev))
    return listings

# Get the keywords from the reviews
def get_most_significant_words(reviews, review_listing_id):

    listings = convert_review_to_text_blobs(reviews)
    selected_reviews = listings[review_listing_id]

    sorted_scores = []

    listing_ids = listings.keys()
    # Compare the selected reviews to the other listings and extract the
    # keywords
    for j in range(NUM_TF_IDF_ITERATIONS):
        comparison_reviews = []
        comparison_review_count = 0
        shuffle(listing_ids)
        for listing_id in listing_ids:
            if listing_id == review_listing_id:
                continue
            if comparison_review_count == NUM_COMPARISON_REVIEWS:
                break
            if len(listings[listing_id]) > MIN_REVIEW_COUNT:
                comparison_reviews += listings[listing_id]
                comparison_review_count += 1
        # Calculate the TF-IDF score for each word in the reviews
        for i, review in enumerate(selected_reviews):
            scores = {word: tfidf(word, review, comparison_reviews) for word in review.words}
            sorted_scores = sorted(scores.items()+sorted_scores, key=lambda x: x[1], reverse=True)

    return sorted(set(sorted_scores), key=sorted_scores.index)[:5]

# Get the correlation score for two reviews
def get_correlation_score(r1, r2, keywords):
    synsets = []
    score = 0
    hits = []

    # Need to lowercase everything for comparison
    r1_lowercase = r1.lower()
    r2_lowercase = r2.lower()

    # Get the synsets for the keywords
    for keyword in keywords:
        synonyms = wn.synsets(keyword)
        synsets.append((keyword, set(chain.from_iterable([word.lemma_names() for word in synonyms]))))

    num_keyword_hits = 0
    # Count the number of times a review has the keywords or synsets of the
    # keywords
    for keyword, lemmas in synsets:
        r1_hits = []
        r2_hits = []
        for synonym in lemmas:
            if synonym in r1_lowercase:
                r1_hits.append(synonym)
            if synonym in r2_lowercase:
                r2_hits.append(synonym)
        if len(r1_hits) > 0 and len(r2_hits) > 0:
            num_keyword_hits += 1
            hits.append((keyword, r1_hits, r2_hits))
        # Update the score
        score += num_keyword_hits * (len(keywords) - keywords.index(keyword))

    score = num_keyword_hits
    return score, hits

# Sample usage:
# Only used for testing, actual usage can be found in grammarBasedRL.py
if __name__ == '__main__':
    listings = parsing.parse_reviews('data/reviews.csv', 1000, 10)
    random_id = listings.keys()[randint(0, len(listings.keys())-1)]
    keywords = get_most_significant_words(listings, random_id)
    results = []
    listing_count = 0
    total = len(listings)
    for listing_id in listings:
        if listing_count == MAX_SAMPLE_LISTINGS:
            break
        if len(listings[listing_id]) < MIN_REVIEW_COUNT:
            continue
        listing_count += 1
        print('Processing listing %s (%d/%d)...' % (listing_id, listing_count, MAX_SAMPLE_LISTINGS))
        comparison_count = 0
        for i in range(len(listings[listing_id])):
            for j in range(len(listings[listing_id])):
                if i == j or comparison_count > MAX_COMPARISONS_PER_LISTING:
                    continue
                review1 = ' '.join([' '.join(sentence) for sentence in parsing.parse_sentences(listings[listing_id][i])])
                review2 = ' '.join([' '.join(sentence) for sentence in parsing.parse_sentences(listings[listing_id][j])])

                correlation_score, hits = get_correlation_score(str(review1), str(review2), zip(*keywords)[0])
                results.append((listing_id, i, j, correlation_score, hits))

                comparison_count += 1

    results.sort(key = lambda r: r[3], reverse=True)
    for i in range(MAX_SAMPLE_RESULTS):
        listing_id, i, j, correlation_score, hits  = results[i]
        review1 = listings[listing_id][i]
        review2 = listings[listing_id][j]
        print 'Review 1) ', review1
        print 'Review 2) ', review2
        print('Correlation score: %f' % (correlation_score))
        print('Hits (Keyword / Review 1 hits / Review 2 hits):')
        for hit in hits:
            keyword, r1_hits, r2_hits = hit
            print keyword, ' / ', r1_hits, ' / ', r2_hits
        print('')
