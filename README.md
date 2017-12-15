CS221 Project: Generating Airbnb Meta-Reviews

Sophia Chen (schen10), Aaron Effron (aeffron), Keshav Santhanam (keshav2)

CS 221, December 2017

FILES

- baseline.py: Implementation of baseline algorithm, by which random sentences with significant words (calculated from TF-IDF) are chosen from reviews to create a meta-review.  Run as:
python baseline.py
- bigrams.py: Find all bigrams present in the review set, and generate both the n-gram dictionary (with weights for reinforcement learning) as well as the grammar dictionary (without weights for part of speech sequence population).  Run as:
python bigrams.py
- grammarBasedRL.py: The base grammar is generated, which is the grammar dictionary or CFG (which we no longer use).  Furthermore this is where the reinforcement learning algorithm is defined, by which we generate sentences and update weights based on calculated correlation scores.  Run as:
python grammarBasedRL.py

