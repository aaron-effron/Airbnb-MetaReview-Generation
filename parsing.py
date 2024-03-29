import csv
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
from langdetect import detect, lang_detect_exception

PUNCTUATION_LIST = ['.',',','?','!',"'",'"',':',';','-', ')', '(', '``', '\'\'','--']

# Parse in the reviews from the .csv file
def parse_reviews(file, num_reviews, num_listings, mandatory_listing):
    reviews = {}
    review_counts = {}

    # We have finished parsing if we have enough listings for TF-IDF and
    # we have gotten the listing we want
    def check_finished_parsing(review_counts):
        if len(review_counts.keys()) < num_listings or mandatory_listing not in review_counts:
            return False
        if review_counts[mandatory_listing] < num_reviews:
            return False
        for listID in review_counts:
            if review_counts[listID] >= num_reviews:
                return True
        return False

    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if check_finished_parsing(review_counts):
                break
            # Decode the review
            review = row['comments'].decode('utf-8')
            # Make sure the review is in English
            try:
                if detect(review) != 'en':
                    continue
            except lang_detect_exception.LangDetectException:
                continue
            # Replace all periods so that we can detect them later (removal of
            # ellipses in punctuation)
            review = review.replace('.', '. ')
            listID = row['listing_id']

            # If we are almost full for number of listings, keep going until
            # we find the mandatory listing
            if mandatory_listing not in reviews and listID != mandatory_listing and len(reviews.keys()) == num_listings-1:
                continue
            # Add the review to the appropriate listing
            if listID not in reviews and len(reviews.keys()) < num_listings:
                reviews[listID] = []
                review_counts[listID] = 0
            if listID in reviews and len(reviews[listID]) < num_reviews:
                reviews[listID].append(review)
                review_counts[listID] += 1
    return reviews

#Function to deal with contractions as well as lower case i
def tokenModifications(token) :
    token = token.replace('n\'t', ' not')
    token = token.replace('\'ve', ' have')
    token = token.replace('\'ll', ' will')
    token = token.replace('\'d', ' would')
    token = token.replace('\'re', ' are')
    token = token.replace('\'s', ' is')
    token = token.replace('\'m', ' am')
    token = token.replace('airbnb\'ers', 'airbnbers')
    if token == 'i' : #Upper case I is properly tagged, whereas lower case is not
        token = "I"
    return token

# Takes a review and parses the sentences into the format desired
def parse_sentences(review):
    sentences = []
    rparts = sent_tokenize(review)
    # Only keep non-punctuation words
    for sent in rparts:
        words = word_tokenize(sent)
        words = [x for x in words if x not in PUNCTUATION_LIST]
        if words == []:
            continue

        # Words to delete due to unicode characters or contractions
        to_delete = []
        for w in range(len(words)):
            if repr(words[w]).find('\u2026') != -1 : #unicode character
                index = repr(words[w]).find('\u2026')
                words[w] = words[w][:index - 2] #... character
            if words[w].find(u'\xb4') != -1: #unicode character
                words[w] = words[w].replace(u'\xb4', '\'')

            #Cafe with the accent
            words[w] = words[w].replace(u'\xe9', 'e')

            if words[w] == '\'s' and words[w-1] == 'there' and w != 0:
                words[w-1] = 'there\'s'
                to_delete.append(w)
            elif words[w] == '\'s' and w != 0:
                to_delete.append(w)
                to_delete.append(w-1)
            words[w] = tokenModifications(words[w])

        # Delete the words we found above
        numIter = 0
        for num in to_delete:
            # numIter is crucial, since the array changes when we delete
            del words[num-numIter]
            numIter += 1
        sentences.append(words)
    return sentences
