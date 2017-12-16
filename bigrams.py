import csv
from nltk import word_tokenize, pos_tag
from nltk.util import ngrams
from nltk.tokenize import sent_tokenize, RegexpTokenizer
from collections import Counter
from langdetect import detect, lang_detect_exception
from parsing import parse_sentences, parse_reviews

REVIEW_COUNT = 100
COMPARISON_LISTING_COUNT = 5

# Find the bigrams within the review file.
# Args:
#	file: path to reviews.csv file
#	nplus: number of "pre" bigram words to take, i.e. if nplus = 4 then final
#		bigram_n_prob would have a key of 3 words, and values of POS
#		dictionaries with the "added" word
#	num_reviews: number of reviews to go through within the file
def find_bigrams(reviews, nplus, listID):
	# Bigram probabilities
	bigram_prob = {}
	# Intermediate variable to store bigram variables
	bigram_counts = Counter()
	# Intermiediate variable to store word count
	word_counts = Counter()
	# Final bigram probabilities that take into account a set of n words
	bigram_n_prob = {}
	# Grammar dictionary
	grammar_dict = {}

	for review in reviews[listID]:
		sents = parse_sentences(review)
		for words in sents:
			# Add tuples of ('-BEGIN-', '-BEGIN-') to match the other POS tuples
			# First part of tuple is the word, second part is the POS tag of
			# that word
			# POS tag of '-BEGIN-' is '-BEGIN-'
			words = [word for word in words if word != '']
			tags = [(u'-BEGIN-', '-BEGIN-')]*(nplus-1) + pos_tag(words)
			words = [u'-BEGIN-']*(nplus-1) + words
			bigrams = ngrams(words, 2)
			bigram_counts += Counter(bigrams)
			word_counts += Counter(words)
			for j in range(len(words) - nplus + 1):
				# POS tag last word since it's "added"
				# Need to make the word a list since if we just
				# pass in a word, pos_tag will decompose it into
				# individual letters
				wordL = []
				wordL.append(words[j+nplus-1])
				(tag_word, POS) = tags[j+nplus-1]
				POS = POS.replace('$','')
				if tag_word != wordL[-1]:
					raise ValueError('POS tagging does not match current word')
				# key is first 3 words (nplus = 4)
				key = tuple(words[j:j+nplus-1])

				# Create bigram  dictionary entry
				if key not in bigram_n_prob:
					bigram_n_prob[key] = {POS:[words[j+nplus-1]]}
				else:
					if POS not in bigram_n_prob[key]:
						bigram_n_prob[key][POS] = []
					bigram_n_prob[key][POS].append(words[j+nplus-1])

				# Create grammar dictionary entry
				gkey = tuple([gram[1].replace('$','') for gram in tags[j:j+nplus-1]])
				if gkey not in grammar_dict:
					grammar_dict[gkey] = [POS]
				else:
					if POS not in grammar_dict[gkey]:
						grammar_dict[gkey].append(POS)
			# Take last few tags of previous key and add on most recent tag
			# This will be the key for the end of the sentence
			# Value of this will be '.' to indicate the end of the sentence
			end_key = gkey[1:] + (POS,)
			if end_key not in grammar_dict:
				grammar_dict[end_key] = []
			if '.' not in grammar_dict[end_key]:
				grammar_dict[end_key].append('.')

	for bigram in bigram_counts:
		if bigram[0] not in bigram_prob:
			bigram_prob[bigram[0]] = {}
		# Treating bigram probability as bigram count/unigram count of first word
		# (some paper said this was the right way to calculate bigram probability)
		bigram_prob[bigram[0]][bigram[1]] = float(bigram_counts[bigram])/word_counts[bigram[0]]

	# Compile n-gram dictionary using bigram probabilities
	for ngram in bigram_n_prob:
		begin = ngram[-1]
		for POS in bigram_n_prob[ngram]:
			new_bigrams = {}
			for word in bigram_n_prob[ngram][POS]:
				new_bigrams[word] = bigram_prob[begin][word]
			bigram_n_prob[ngram][POS] = new_bigrams

	return bigram_n_prob, grammar_dict

# Used to individually test the bigram dictionary
if __name__ == '__main__':
	reviews = parse_reviews('data/reviews.csv', REVIEW_COUNT, COMPARISON_LISTING_COUNT+1)
	b, g = find_bigrams(reviews, 4, '1178162')
