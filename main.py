#!/usr/bin/python

import sys
import operator
import time
import datetime
from Article import Article
from Article_List import Article_List
import tickers
import zergwatch
import streetupdates
import newsoracle
import smarteranalyst
import streetinsider
import json
import web
import xml.etree.ElementTree as ET
#import aomarkets
#import marketwatch
#import investorplace
import dominate
from dominate.tags import *
from StockInfo import StockInfo

class form:
    form = web.form.Form(
        web.form.Checkbox('zergwatch', value=True),
        web.form.Checkbox('streetupdates', value=True),
        web.form.Checkbox('newsoracle', value=True),
        web.form.Checkbox('smarteranalyst', value=True),
        web.form.Checkbox('streetinsider', value=True),
        web.form.Dropdown('days', args=['1', '2', '3', '4', '5']),
        web.form.Button('Post entry')
    )

    # GET method is used when there is no form data sent to the server
    def GET(self):
        form = self.form()
        return render.form(form)

    def POST(self):
        form = self.form()
        if not form.validates():
            print 'uh oh'
        raise web.seeother('/success')


if __name__ == "__main__":

    # Eric, change this if you dont want to use the server for inputs
    server = False

    # For Justin's stock data analytics testing
    #TickerInfo.get_info('MSTX')


    urls = (
        '/articles', 'form'
    )
    render = web.template.render('templates/')
    app = web.application(urls, globals())
    if server:
        app.run()

    # Ask user what sites they want to search
    prompt = 'Which site(s) do you want to search?\n[1] zergwatch\n[2] streetupdates' + \
    '\n[3] newsoracle\n[4] smarteranalyst\n[5] streetinsider !!\n\nEnter number(s): '
    response_list = raw_input(prompt).split(' ')

    # Have user input number of days worth of articles they want to search
    print ''
    var = raw_input("How many days back do you want to search? ")
    days_to_search = int(float(var))

    # Have user input number of top tickers they're interested in for the run
    print ''
    var = raw_input("How many top tickers do you want to learn about? ")
    num_top_tickers = int(float(var))
    print ''

    # Start timer
    start_time = time.time()

    # Create master tickers list
    master_articles = Article_List()
    sites_searched = []

    #########################################################################
    #########################################################################
    # Search zergwatch.com and get all articles within past 'days_to_search'
    if '1' in response_list:
        sites_searched.append('zergwatch')
        zergwatch_articles = zergwatch.search(days_to_search)
    else:
        zergwatch_articles = Article_List()

    #########################################################################
    #########################################################################
    # Search streetupdates.com and get all articles within past 'days_to_search'
    if '2' in response_list:
        sites_searched.append('streetupdates')
        streetupdates_articles = streetupdates.search(days_to_search)
    else:
        streetupdates_articles = Article_List()

    #########################################################################
    #########################################################################
    # Search newsoracle.com and get all articles within past 'days_to_search'
    if '3' in response_list:
        sites_searched.append('newsoracle')
        newsoracle_articles = newsoracle.search(days_to_search)
    else:
        newsoracle_articles = Article_List()

    #########################################################################
    #########################################################################
    # Search smarteranalyst.com and get all articles within past 'days_to_search'
    if '4' in response_list:
        sites_searched.append('smarteranalyst')
        smarteranalyst_articles = smarteranalyst.search(days_to_search)
    else:
        smarteranalyst_articles = Article_List()

    #########################################################################
    #########################################################################
    # Search streetinsider.com and get all articles within past 'days_to_search'
    if '5' in response_list:
        sites_searched.append('streetinsider')
        streetinsider_articles = streetinsider.search(days_to_search)
    else:
        streetinsider_articles = Article_List()

    #########################################################################
    #########################################################################
    # Add all returned articles to master Article_List object
    for article in zergwatch_articles.articles:
        master_articles.add_article(article)
    for article in streetupdates_articles.articles:
        master_articles.add_article(article)
    for article in newsoracle_articles.articles:
        master_articles.add_article(article)
    for article in smarteranalyst_articles.articles:
        master_articles.add_article(article)
    for article in streetinsider_articles.articles:
        master_articles.add_article(article)

    #########################################################################
    #########################################################################
    # Save all articles to a file for later reference
    sites_searched_string = "_".join(sites_searched)
    file_name = 'previous-runs/{0}_{1}.txt'.format(datetime.date.today(), sites_searched_string)
    f = open(file_name, 'w')
    f.write('Run date: {0}\n'.format(datetime.date.today()))
    f.write('Searched back to: {0}\n'.format(datetime.date.today() - datetime.timedelta(days=days_to_search)))
    f.write('Sites searched: {0}\n'.format(sites_searched))
    f.write('Total articles: {0}\n'.format(len(master_articles)))
    f.write('Top {0} most common tickers:\n'.format(str(num_top_tickers)))
    top_tickers = master_articles.return_top(num_top_tickers)
    for item in top_tickers:
        f.write('{0}:\t{1}\n'.format(item[0], item[1]))
    f.write('')
    f.write(str(master_articles))
    f.close()

    #########################################################################
    #########################################################################
    # Print stock stats and article details for user specified number of top tickers
    num_total_tickers = len(master_articles.count_tickers())
    n = 0
    with open('latesttoptickers.txt', 'w') as f2:
        sys.stdout = f2
        print 'Top {0} most common tickers:'.format(str(num_top_tickers))
        for item in top_tickers:
            print '{0}:\t{1}'.format(item[0], item[1])
        for item in top_tickers:
            n += 1
            print '\n-----------------------------------------------------------'
            print '[#{0} / {1} total tickers] {2}'.format(n, num_total_tickers, item[0])
            print '-----------------------------------------------------------\n'
            print '-----------------------------'
            print 'Stock info for {0} at {1}'.format(item[0], str(datetime.datetime.now()))
            print '-----------------------------'
            stock_info = StockInfo(item[0])
            print stock_info
            print '-----------------------------'
            print 'All {0} articles for {1}'.format(item[1], item[0])
            print '-----------------------------'
            print master_articles.all_for_ticker(item[0])
    f2.close()
    sys.stdout = sys.__stdout__

    #########################################################################
    #########################################################################
    # Get stock info for user specified number of top tickers (highest recurring)
    #print ""
    #print "--------------------------"
    #print 'Info for top {0} most common tickers:'.format(str(num_top_tickers))
    #print "--------------------------\n"
    #for item in top_tickers:
    #    stock_info = StockInfo(item[0])
    #    print "--------------------------"
    #    print stock_info

    #########################################################################
    #########################################################################
    # Kyle's testing
    #f.write('\n----------------------------\n----------------------------\n\n')
    #f.write('Kyle Tests\n')
    #print master_articles.to_JSON()
    #f.write(master_articles.to_JSON())

    # Kyle's html printing
    #doc = dominate.document(title='Articles')
    #with doc:
    #    with div():
    #        ul(li(a(article.name, href=article.href), __pretty=False) for article in master_articles.articles)
    #print doc
    #with open('articles.html', 'w') as f:
    #    f.write(doc.render())




    #########################################################################
    #########################################################################
    # End timer and print total time elapsed
    end_time = time.time()
    hours, rem = divmod(end_time - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print ""
    print "----------------------------"
    print"Run time: ", "{:0>2}:{:05.2f}".format(int(minutes),seconds)
    print "----------------------------"
