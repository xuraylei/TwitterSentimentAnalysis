#! /usr/bin/python

from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from math import sqrt

import sys
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

def main(argv):
    mode = 'overall'  # we support three modes: overall for all candidates, time for time series analysis for a candidate, query for one candidate via Solr
    keyword = None 
    if len(argv) == 1:
        mode = argv[0];
    elif len(argv) == 2:
        mode = argv[0]
        keyword = argv[1]

    if mode == 'overall' or  mode == 'time':
        loadFromCSV()
    elif mode == 'query':
        searchFromSolr(keyword,'http://localhost:8983/solr/tweets/')
     
    sentiAnalyze()
    visualization(mode,keyword)
    #display()
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


def visualization(opt, candidate = None):
    import numpy as np
    import matplotlib.pyplot as plot

    if opt == 'overall':
        candidate_num = 5
        index = np.arange(candidate_num)

        cand = ('Bernie Sanders', 'Donald Trump', 'Hillary Rodham Clinton', 'John Kasich', 'Ted Cruz')
        n_group = 5

        bar_width = 0.35
        opacity = 0.4 

        candidate_pos = []
        candidate_neg = []
        for candidate in cand:
            candidate_pos.append(result['pos'][candidate]['total'])
            candidate_neg.append(result['neg'][candidate]['total'])

        candidate_pos = tuple(candidate_pos)
        candidate_neg = tuple(candidate_neg)

        rects1 = plot.bar(index, candidate_pos, bar_width, alpha = opacity,
            color = 'b', label = 'positive')
        rects2 = plot.bar(index + bar_width, candidate_neg, bar_width, alpha = opacity,
        color = 'r', label = 'negative')

        plot.xlabel('Candidate')
        plot.ylabel('tweets')
        plot.title('Positive and Negative tweets for president candidate in 2016')
        plot.xticks(index + bar_width, cand)
        plot.legend()
        plot.tight_layout()
    elif opt == 'time':
        week_num = 4
        index = np.arange(week_num)

        week = ('week1', 'week2', 'week3', 'week4')
        w_group = 4

        bar_width = 0.35
        opacity = 0.4

        week_positive = []
        week_negative = []
        #normalize the sentiment counts 
        for w in week:
            week_positive.append(result['pos'][candidate][w]/sqrt(result['pos'][candidate]['total']))
            week_negative.append(result['neg'][candidate][w]/sqrt(result['neg'][candidate]['total']))

        plot.bar(index, week_positive, bar_width, color = 'b', label = 'positive')
        plot.bar(index+bar_width, week_negative, bar_width, color = 'r', label = 'negative')

        plot.xlabel('Week')
        plot.ylabel('tweets')
        plot.title('Positive and Negative tweets (normalized) for' + candidate + ' in four weeks data set')
        plot.xticks(index + bar_width, week)
        plot.legend()


    elif opt == 'query':
        
        labels = ('positive', 'negative', 'neutral')
        fracs = [15,40,45]
        color = ['blue', 'red', 'lightcoral']
        explode = (0, 0.1, 0)
        plot.pie(fracs, explode=explode, labels=labels,autopct='%1.1f%%', shadow=True, startangle=90)
        plot.title('The setiment analysis for candidate ' + candidate)
    
    plot.show()
    return

def getWords(text):
    import re
    return re.compile('\w+').findall(text)

#retrieve data from Solr server
def searchFromSolr(keyword, url):
    url += 'select?q='
    # parse words from option
    words = getWords(keyword)
    if len(words) == 1:
        url +=  words[0]
    else:
        url += words[0]
        for e in words[1:]:
            url = url + '+' + e
    url += '/%0A&wt=csv&indet=true&rows=100000'   
    print url
    import urllib2

    request = urllib2.Request(url)
    response = urllib2.urlopen(request).read()

    
    if keyword not in tweets:
        tweets[keyword] = {}
    if 'solr' not in tweets[keyword]:
        tweets[keyword]['solr'] = []


    for line in response.splitlines():
        tweet = line.split(',')
        tweets[keyword]['solr'].append(tweet)
    


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
    main(sys.argv[1:])
