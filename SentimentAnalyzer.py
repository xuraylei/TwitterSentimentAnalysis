#! /usr/bin/python

from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import os
import glob
import csv

#if |positive_score - negative_core| > DISTINCT_THREASHOLD, we consider people have attitude towards to event
DISTINCT_THRESHOLD = 0.3

tweets = {}

pos_tweets = {}
neg_tweets = {}

#summary result
result = {}
result['sum'] = {}  #statistics for all tweets
result['pos'] = {}  #statistics for positive tweets
result['neg'] = {}  #statistics for negative tweets

def main():
    
    loadFromCSV()
    sentiAnalyze()
    display()
    return


def sentiAnalyze():
    analyzer = SentimentIntensityAnalyzer()


    for candidate in tweets:
        for week in tweets[candidate]:
            for tweet in tweets[candidate][week]:
                if candidate not in result['sum']:
                    result['sum'][candidate] = {}
                if 'total' not in result['sum'][candidate]:
                    result['sum'][candidate]['total'] = 0
                if week not in result['sum'][candidate]:
                    result['sum'][candidate][week] = 0

                result['sum'][candidate][week] += 1
                result['sum'][candidate]['total'] += 1


                score = analyzer.polarity_scores(tweet[2])
                if (score['pos'] - score['neg']) > DISTINCT_THRESHOLD:
                    if candidate not in pos_tweets:
                        pos_tweets[candidate] = {}
                    if week not in pos_tweets[candidate]:
                        pos_tweets[candidate][week] = []
                    pos_tweets[candidate][week].append(tweet)
                   
                    if candidate not in result['pos']:
                        result['pos'][candidate] = {}
                    if 'total' not in result['pos'][candidate]:
                        result['pos'][candidate]['total'] = 0
                    if week not in result['pos'][candidate]:
                        result['pos'][candidate][week] = 0
                    result['pos'][candidate][week] += 1
                    result['pos'][candidate]['total'] += 1

                if (score['neg'] - score['pos']) > DISTINCT_THRESHOLD:
                    if candidate not in neg_tweets:
                        neg_tweets[candidate] = {}
                    if week not in neg_tweets[candidate]:
                        neg_tweets[candidate][week] = []
                    neg_tweets[candidate][week].append(tweet)

                    if candidate not in result['neg']:
                        result['neg'][candidate] = {}
                    if 'total' not in result['neg'][candidate]:
                        result['neg'][candidate]['total'] = 0
                    if week not in result['neg'][candidate]:
                        result['neg'][candidate][week] = 0
                    result['neg'][candidate][week] += 1
                    result['neg'][candidate]['total'] += 1

    return

def display():
    print 'The summary for data set:'
    for candidate in tweets:
        print 'The total number of tweets for ' + candidate + ' ' + str(result['sum'][candidate]['total'] + result['neg'][candidate]['total'])
 
    for candidate in result['pos']:
        print '--------------------------------------'
        print 'The summary positive result for ' + candidate
        for week in result['pos'][candidate]:
            print week + ' : ' + str(result['pos'][candidate][week])

    for candidate in result['neg']:
        print '--------------------------------------'
        print 'The summary negative result for ' + candidate
        for week in result['neg'][candidate]:
            print week + ' : ' + str( result['neg'][candidate][week])

    for candidate in pos_tweets:
        for week in pos_tweets[candidate]:
            print '--------------------------------'
            print 'positive tweets for' + candidate + ' in ' + week 
            for tweet in pos_tweets[candidate][week]:
                print tweet
            print '--------------------------------'
            print 'negative tweets for' + candidate + ' in ' + week
            for tweet in neg_tweets[candidate][week]:
                print tweet
    return

def saveResult():
    return

def loadFromCSV():
    for root, dirs, files in os.walk('data'):
        for dir in dirs:
            path = os.path.join(root, dir)
            for file in glob.glob(path + '/*.csv'):
                #print file
                with open(file, 'rb') as csvfile:
                    time = csvfile.name.split('/')[1]
                    name = csvfile.name.split('/')[-1].split('.')[0]
                    if name not in tweets:
                        tweets[name] = {}
                    if time not in tweets[name]:
                        tweets[name][time] = []

                    reader = csv.reader(csvfile)
                    for row in reader:
                        tweet = list(row)
                        tweets[name][time].append(tweet)
    return

#remove duplicated tweets in the data set
def dedup(tweets):
    return


if __name__ == "__main__":
    main()
