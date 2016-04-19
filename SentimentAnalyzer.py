#! /usr/bin/python

from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import glob
import csv

#if |positive_score - negative_core| > DISTINCT_THREASHOLD, we consider people have attitude towards to event
DISTINCT_THRESHOLD = 0.3

tweets = []

pos_tweets = []
neg_tweets = []

def main():
    
    loadFromCSV()
    sentiAnalyze()
    display()
    return


def sentiAnalyze():
    analyzer = SentimentIntensityAnalyzer()

    for tweet in tweets:
        score = analyzer.polarity_scores(tweet[2])
        #print tweet[2] 
        #print score
        if (score['pos'] - score['neg']) > DISTINCT_THRESHOLD:
            pos_tweets.append(tweet)
        if (score['neg'] - score['pos']) > DISTINCT_THRESHOLD:
            neg_tweets.append(tweet)

    return

def display():
    print '--------------------------------'
    print 'positive tweets:'
    for tweet in pos_tweets:
        print tweet
    print '--------------------------------'
    print 'negative tweets:'
    for tweet in neg_tweets:
        print tweet
    return

def loadFromCSV():
    tweet_count = 0
    for file in glob.glob('data/*.csv'):
        with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                tweet = list(row)
                tweet_count += 1
                tweets.append(tweet)
             #   print tweet
             #   print '\n'
    print 'The numer of tweets is ' + str(len(tweets))
    return

#remove duplicated tweets in the data set
def dedup(tweets):
    return


if __name__ == "__main__":
    main()
