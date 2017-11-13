import csv
from nltk import word_tokenize, pos_tag
from nltk.util import ngrams
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from collections import Counter

# Find the bigrams within the review file. 
# Args:
#	file: path to reviews.csv file
#	nplus: number of "pre" bigram words to take, i.e. if nplus = 4 then final
#		bigram_n_prob would have a key of 3 words, and values of POS dictionaries
#		with the "added" word
#	num_reviews: number of reviews to go through within the file
def find_bigrams(file, nplus, num_reviews)
	# Bigram probabilities
	bigram_prob = {}
	# Intermediate variable to store bigram variables
	bigram_counts = Counter()
	# Intermiediate variable to store word count
	word_counts = Counter()
	# Final bigram probabilities that take into account a set of n words
	bigram_n_prob = {}

	# Tokenizer to find words but ignore any punctuation other than ' for 
	# contractions
	tokenizer = RegexpTokenizer(r"\w+'*\w*")

	# should maybe check for validity of file but that can be dealt with later
	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		i = 0
		for row in reader:
			if i == num_reviews:
				break
			review = '-BEGIN- '+row['comments']
			print review
			rparts = sent_tokenize(review)
			for sent in rparts:
				words = tokenizer.tokenize(sent)
				bigrams = ngrams(words, 2)
				bigram_counts += Counter(bigrams)
				word_counts += Counter(words)
				for i in range(len(words) - nplus):
					# POS tag last word since it's "added"
					POS = pos_tag(words[i+nplus-1])[0][1]
					# key is first 3 words (nplus = 4)
					key = tuple(words[i:i+nplus-1])
					if key not in bigram_n_prob:
						bigram_n_prob[key] = {POS:[words[i+nplus-1]]}
					else:
						if POS not in bigram_n_prob[key]:
							bigram_n_prob[key][POS] = []
						bigram_n_prob[key][POS].append(words[i+nplus-1])
			i += 1

					

	for bigram in bigram_counts:
		if bigram[0] not in bigram_prob:
			bigram_prob[bigram[0]] = {}
		# Treating bigram probability as bigram count/unigram count of first word
		# (some paper said this was the right way to calculate bigram probability)
		bigram_prob[bigram[0]][bigram[1]] = float(bigram_counts[bigram])/word_counts[bigram[0]]
	for ngram in bigram_n_prob:
		begin = ngram[-1]
		for POS in bigram_n_prob[ngram]:
			new_bigrams = {}
			for word in bigram_n_prob[ngram][POS]:

				new_bigrams[word] = bigram_prob[begin][word]
			bigram_n_prob[ngram][POS] = new_bigrams
	print bigram_n_prob
	return bigram_n_prob

if '__name__' == '__main__':
	find_bigrams('boston-airbnb-open-data\\reviews.csv', 4, 100)
