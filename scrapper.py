#!/usr/bin/python

import requests
import bs4
import sys
import re
import os
import urlparse
import json
import pickle
import time
import datetime
from decimal import *
import hashlib

def main(argv):

	for url in Configuration.categories:
		#parse all pages from given category
		listings = parse_category(url);

		#load existing listings
	  	pickle_listings = pickle.load( open( Configuration.pickle_db, "rb" ) )

	  	log('db count start - ' + str(len(pickle_listings)))

	  	#add new listings into db
	  	for listing in listings:
	  		if listing not in pickle_listings:
	  			pickle_listings[listing]= listings.get(listing)

	  	#save listings
		pickle.dump(pickle_listings, open( Configuration.pickle_db, "wb" ))

	  	log('db count end - ' + str(len(pickle_listings)))

def parse_category(category_url):
	page = 1

	log(category_url)

	#parse first page
	listings = parse_page(category_url)
	
	#contineue to parse if there is any result in first page
	pageExists = len(listings)>0
	while pageExists:
		#update url > replace old page with new
		category_url = category_url.replace('page=' + str(page), 'page=' + str(page+1))
		page= page+1

		log('fetch - ' + category_url)

		#parse next page
		current_page_listings = parse_page(category_url)

  		log('results - ' + str(len(current_page_listings)))

		pageExists = len(current_page_listings)>0


		#merge current page into list
  		listings = dict(listings.items() + current_page_listings.items())

  	return listings

def parse_page(url):
	response = requests.get(url)

	#cancel parsing if page doesnt exists
	if response.status_code is not 200:
		return

	soup = bs4.BeautifulSoup(response.text)

	#select all listings from lise, execlude adds
	results = soup.select('#resultlist .clearfix')
	
	listings={}
	for result in results:
		listing = parse_listing(result)
		if listing is not type(None):
			hash = listing['hash']=hashlib.sha224(listing['url']).hexdigest()
			listings[hash]=listing
	
	return listings

def parse_listing(result):
	listing={}
	number_pattern = re.compile(r'[0-9]+(\.[0-9]+)?')

	title = result.select('h2 a')
	if title:
		listing['title'] =title[0].get_text()
		listing['url'] =  'http://www.willhaben.at' + title[0]['href']
		

	listing['size'] = -1
	size = result.select('.size')[0].get_text().strip()
	if len(size)>0:
		listing['size'] = number_pattern.search(size).group(0)

	listing['price'] = -1
	price =  result.select('.price')[0].get_text().strip()
	if len(price)>0:
		listing['price'] = str(number_pattern.search(price).group(0)).replace('.','')

	address = result.select('.location')[0].get_text().replace("\r\n","").split()
	listing['bezirk'] = address[0]

	listing['created'] = str(datetime.datetime.utcnow())

	return listing

class Configuration(object):
	pickle_db = 'willhaben.p'
	categories = ['http://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1020-leopoldstadt?areaId=117224&parent_areaid=900&page=1'
				'http://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1030-landstrasse?areaId=117225&parent_areaid=900&page=1',
				'http://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1040-wieden?areaId=117226&parent_areaid=900&page=1',
				'http://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1050-margareten?areaId=117227&parent_areaid=900&page=1',
				'http://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1060-mariahilf?areaId=117228&parent_areaid=900&page=1',
				'http://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1070-neubau?areaId=117229&parent_areaid=900&page=1',
				'http://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1080-josefstadt?areaId=117230&parent_areaid=900&page=1',
				'http://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1090-alsergrund?areaId=117231&parent_areaid=900&page=1']

def log(message):
	print str(datetime.datetime.utcnow()) + ' - ' + message

if __name__ == "__main__":
   main(sys.argv[1:])