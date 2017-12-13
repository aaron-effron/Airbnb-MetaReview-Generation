import csv
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
from langdetect import detect, lang_detect_exception

PUNCTUATION_LIST = ['.',',','?','!',"'",'"',':',';','-', ')', '(', '``', '\'\'','--']

def parse_reviews(file, num_reviews, num_listings, mandatory_listing):
    reviews = {}
    review_counts = {}

    def check_finished_parsing(review_counts):
        if len(review_counts.keys()) < num_listings or mandatory_listing not in review_counts:
            return False
        if review_counts[mandatory_listing] < num_reviews:
            return False
        print review_counts[mandatory_listing]
        for listID in review_counts:
            if review_counts[listID] >= num_reviews:
                return True
        return False

    # should maybe check for validity of file but that can be dealt with later
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if check_finished_parsing(review_counts):
                break

            review = row['comments'].decode('utf-8')
            try: 
                if detect(review) != 'en':
                    continue
            except lang_detect_exception.LangDetectException:
                continue
            review = review.replace('.', '. ')
            listID = row['listing_id']
            if mandatory_listing not in reviews and listID != mandatory_listing and len(reviews.keys()) == num_listings-1:
                continue
            if listID not in reviews and len(reviews.keys()) < num_listings:
                reviews[listID] = []
                review_counts[listID] = 0
            if listID in reviews and len(reviews[listID]) < num_reviews: #TODO: This should be else
                reviews[listID].append(review)
                review_counts[listID] += 1
    return reviews


#Function to deal with contractions as well as lower case i
def tokenModifications(token) :
    token = token.replace('n\'t', ' not')
    token = token.replace('\'ve', ' have')
    token = token.replace('\'ll', ' will')
    token = token.replace('\'d', ' would')
    token = token.replace('\'s', ' is')
    token = token.replace('\'m', ' am')
    if token == 'i' : #Upper case I is properly tagged, whereas lower case is not
        token = "I"
    return token


# Takes a review and parses the sentences into the format desired
def parse_sentences(review):
    sentences = []
    rparts = sent_tokenize(review)
    for sent in rparts:
        words = word_tokenize(sent)
        words = [x for x in words if x not in PUNCTUATION_LIST]
        if words == []:
            continue
        
        to_delete = []
        for w in range(len(words)):
            if repr(words[w]).find('\u2026') != -1 : #unicode character that tries to mess everything up
                index = repr(words[w]).find('\u2026')
                words[w] = words[w][:index - 2] #... is stupid
            if words[w].find(u'\xb4') != -1: #unicode character that tries to mess everything up
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
        numIter = 0
        for num in to_delete:
            del words[num-numIter] #numIter is crucial, since the array changes when we delete!!
            numIter += 1 
        sentences.append(words)
    return sentences
