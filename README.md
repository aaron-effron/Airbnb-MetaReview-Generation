**CS221 Project: Generating Airbnb Meta-Reviews**

Sophia Chen (schen10), Aaron Effron (aeffron), Keshav Santhanam (keshav2)

CS 221, December 2017

Our goal is to generate “meta-reviews” of properties listed on Airbnb using real reviews of Boston
properties. These meta-reviews should capture the most relevant features of a property according to the
reviews. We use a Markov decision process (MDP) to generate sentences in our meta-review. Our word
choices for the MDP come from n-grams of the reviews for a single listing, and our grammar structure
is based on the grammar structures found within those reviews. The MDP is run with reinforcement
learning to set n-gram weights in such a way that maximizes correlation to actual reviews in terms of
overlap in significant words and length. With our MDP, we are able to achieve an average rating of 5.386,
on a scale from 1-10, for usefulness of our meta-reviews, which is reasonably close to our human oracle
rating of 8.256.

FILES

- baseline.py: Implementation of baseline algorithm, by which random sentences with significant words (calculated from TF-IDF) are chosen from reviews to create a meta-review.  Run as:
python baseline.py
- bigrams.py: Find all bigrams present in the review set, and generate both the n-gram dictionary (with weights for reinforcement learning) as well as the grammar dictionary (without weights for part of speech sequence population).  This is called in grammarBasedRL.py.  Can also be run as:
python bigrams.py
- grammarBasedRL.py: The base grammar is generated, which is the grammar dictionary or CFG (which we no longer use).  Furthermore this is where the reinforcement learning algorithm is defined, by which we generate sentences and update weights based on calculated correlation scores.  Run as:
python grammarBasedRL.py
- parsing.py: Parse csv files and create dictionary of reviews.  This is called in grammarBasedRL.py
- plot.py: Generate explanatory plots.  Run as:
python plot.py
- synset.py: Correlation score calculations using TF-IDF to find most significant words,  find synset distance between them to calculate correlation.  This is called in grammarBasedRL.py
