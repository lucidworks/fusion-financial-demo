#!/usr/local/bin/python3

import csv
import json
import random
import copy
import re
import uuid
from random import getrandbits
from ipaddress import IPv4Address, IPv6Address
import time
import calendar


COMPANY_INPUT_CSV = '../data/Finance/sp500.csv'
SIGNALS_JSON = '../data/Finance/signals.json'

CSV_FIELDS = ['id','timestamp','type']

COMPANY_QUERY_SPECIFIERS = ['earnings', 'next earnings', 'last earnings date', 'eps guidance',
                            'dividend', 'dividend yield', 'share buyback', 'share repurchase',
                            'latest news', 'dividend yield', 'earnings call', 'scandal', 'litigation',
                            '10k', 'annual results', 'quarterly result', 'q1 earnings', 'fy1 earnings',
                            'analyst coverage', 'product launch', 'layoffs']

COMPANIES_LIST = list()

RANDOM_SEED = 123 # Integer. set to None to make script random on every run (using system time)
random.seed(RANDOM_SEED)

USER_IDS = []
for i in xrange(500):
    USER_IDS.append(str(uuid.uuid4()))


with open(COMPANY_INPUT_CSV,'r') as companiesfile:
    companies_reader = csv.DictReader(companiesfile,restkey="state")

    for company_dict in companies_reader:
        COMPANIES_LIST.append(company_dict)

num_queries = 10000
query_id = 0

time_now = int(calendar.timegm(time.gmtime()))

with open(SIGNALS_JSON, 'w') as json_outfile:
    json_outfile.write('[\n')
    days_ago = random.randint(1,90)
    timestamp = time_now - (days_ago * 86400)
    timestamp *= 1000
    while query_id < num_queries:
        session_id = str(uuid.uuid4())
        user_id = random.choice(USER_IDS)
        query_id += 1

        company = COMPANIES_LIST[random.randint(1,500)]
        query = company['ticker'] if random.uniform(0,1) < 0.5 else company['company_name']
        query = query.strip()
        query = re.sub('Inc\.$', '', query)
        query = re.sub('Inc$', '', query)
        query = re.sub('Corp\.$', '', query)
        query = re.sub('Corp$', '', query)
        query = re.sub('Co\.$', '', query)
        query = re.sub('Co$', '', query)
        query = re.sub('Ltd\.$', '', query)
        query = re.sub('Ltd$', '', query)
        query = query.strip()

        if random.uniform(0,1) < 0.3:
            query = query + ' ' + random.choice(COMPANY_QUERY_SPECIFIERS)

        query = query.lower()

        misspelling = False
        if len(query) > 4:
            coin = random.uniform(0,1)
            if coin < 0.05:
                misspelling = True
                index = random.randint(0, len(query) - 2)
                char_list = list(query)
                char_list[index], char_list[index + 1] = char_list[index + 1], char_list[index]
                query = ''.join(char_list)
            elif coin < 0.1:
                misspelling = True
                index = random.randint(0, len(query) - 2)
                query = query[:index] + query[index + 1:]

        bits = getrandbits(32) # generates an integer with 32 random bits
        addr = IPv4Address(bits) # instances an IPv4Address object from those bits
        addr_str = str(addr)

        request_signal = dict()
        request_signal['id'] = query_id
        request_signal['type'] = 'request'
        request_signal['timestamp'] = timestamp
        request_signal['params'] = dict()
        request_signal['params']['user_id'] = user_id
        request_signal['params']['session'] = session_id
        request_signal['params']['query'] = query
        request_signal['params']['app_id'] = 'Finance'
        request_signal['params']['ip_address'] = addr_str
        json.dump(request_signal, json_outfile)
        json_outfile.write(',\n')

        response_signal = dict()
        response_signal['id'] = query_id
        response_signal['type'] = 'response'
        response_signal['timestamp'] = timestamp + random.randint(0,3)
        response_signal['params'] = dict()
        response_signal['params']['user_id'] = user_id
        response_signal['params']['session'] = session_id
        response_signal['params']['query'] = query
        response_signal['params']['query_orig_s'] = query
        response_signal['params']['app_id'] = 'Finance'
        response_signal['params']['ip_address'] = addr_str
        response_signal['params']['response_type'] = 'empty' if misspelling else 'results'
        json.dump(response_signal, json_outfile)
        json_outfile.write(',\n')

        click_signal = dict()
        click_signal['id'] = str(uuid.uuid4())
        click_signal['type'] = 'click'
        click_signal['timestamp'] = timestamp + random.randint(4, 10)
        click_signal['params'] = dict()
        click_signal['params']['fusion_query_id'] = query_id
        click_signal['params']['user_id'] = user_id
        click_signal['params']['session'] = session_id
        click_signal['params']['query'] = query
        click_signal['params']['query_orig_s'] = query
        click_signal['params']['ctype'] = 'result'
        click_signal['params']['app_id'] = 'Finance'
        click_signal['params']['ip_address'] = addr_str
        click_signal['params']['response_type'] = 'empty' if misspelling else 'results'
        click_signal['params']['doc_id'] = company['ticker']
        click_signal['params']['res_pos'] = 1
        json.dump(click_signal, json_outfile)
        if query_id < num_queries:
            json_outfile.write(',\n')
        else:
            json_outfile.write(']\n')
