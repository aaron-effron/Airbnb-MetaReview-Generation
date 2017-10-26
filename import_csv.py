import csv
from collections import defaultdict

uniqueList = []

#All the reviews match with something in listings

with open('listings.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile)#, delimiter=' ', quotechar='|')
	counter = 0
	currentId = 0
	uniqueListings = 0

	minVal = 100
	counter = -1
	revIndex = -1
	scoresDict = defaultdict(float)

	for row in spamreader :
		counter += 1
		uniqueList.append(row[0])
		if counter == 0 :
			revIndex = row.index('review_scores_value')
			continue

		number = -1 if row[revIndex] == '' else int(row[revIndex])
		scoresDict[number] += 1
	
	print scoresDict

with open('reviews.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile)#, delimiter=' ', quotechar='|')
	counter = 0
	currentId = 0
	uniqueListings = 0
	numInRow = 0
	ltf = 0
	for row in spamreader:
		thisId = row[0]
		if thisId != currentId :
			if (numInRow < 3) :
				ltf += 1
			if thisId not in uniqueList :
				print "MAJOR PROBLEM", thisId
			uniqueListings += 1
			currentId = thisId
			numInRow = 0
		counter += 1
		numInRow += 1
		#if (counter >= 2) :
		#	break
		#print ', '.join(row)
	#print counter
	print uniqueListings
	print "Less than five = {}".format(ltf)


seattleUniqueList = []
with open('seattle_listings.csv', 'rb') as csvfile:
	seattlereader = csv.reader(csvfile)#, delimiter=' ', quotechar='|')
	counter = -1
	currentId = 0
	uniqueListings = 0
	numRows = 0
	seattleScoresDict = defaultdict(float)
	revIndex = -1

	for row in seattlereader:
		counter += 1
		if counter == 0 :
			revIndex = row.index('review_scores_value')
			continue
		thisId = row[0]
		seattleUniqueList.append(thisId)
		numRows += 1
		number = -1 if row[revIndex] == '' else int(row[revIndex])
		seattleScoresDict[number] += 1
	print "Num rows = ", numRows
	print seattleScoresDict
	
with open('seattle_reviews.csv', 'rb') as csvfile:
	seattlereader = csv.reader(csvfile)#, delimiter=' ', quotechar='|')
	counter = 0
	currentId = 0
	uniqueListings = 0
	numInRow = 0
	ltf = 0
	for row in seattlereader:
		thisId = row[0]
		if thisId != currentId :
			if (numInRow < 3) :
				ltf += 1
			numInRow = 0
			uniqueListings += 1
			currentId = thisId
		counter += 1
		numInRow+= 1
	print uniqueListings
	print "Less than five = {}".format(ltf)


