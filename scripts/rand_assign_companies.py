#!/usr/local/bin/python3

# This Python script iterates through the S&P 500 ('../data/Finance/sp500.csv') and randomly selects companies for 2 data sets
# 1) Creates 'portfolios' of companies with weights
# 2) Creates sets of 'my companies' for sell side analysts
# Company weights in a portfolio add up to 1. Portfolios belong either to a client or a Portfolio Manager (PM)
# Company weights for sell side analyst have 3 levels (0-2) indicating 'importance'

# Randomly selecting companies may not work since news will likely tag only a few.

# Libraries

import csv
import random

# 'Global' variables

COMPANY_INPUT_CSV = '../data/Finance/sp500.csv'
BUCKETS_CSV = '../data/Finance/company_buckets.csv'

CSV_FIELDS = []

BUCKETS = [
    {'type':'analyst','people':[
        {'owner':'Frank','buckets':[]},
        {'owner':'Geoffrey','buckets':[]},
        {'owner':'Carla','buckets':[]},
        {'owner':'Sophie','buckets':[]}
    ]},
    {'type':'client','people':[
        {'owner':'Robert','buckets':[]},
        {'owner':'Cynthia','buckets':[]}
    ]},
    {'type':'manager','people':[
        {'owner':'Lawson','buckets':[]},
        {'owner':'Chloe','buckets':[]}
    ]}
]

COMPANIES_LIST = list()

RANDOM_SEED = 123 # Integer. set to None to make script random on every run (using system time)
random.seed(RANDOM_SEED)

# global ANALYSTS, CLIENTS, MANAGERS, COMPANIES_DICT # access global variables for modification

# Easiest way is just to read company CSV into list since it is small
with open(COMPANY_INPUT_CSV,'r') as companiesfile:
    companies_reader = csv.DictReader(companiesfile)
    CSV_FIELDS = companies_reader.fieldnames

    for company_dict in companies_reader:
        COMPANIES_LIST.append(company_dict)

# Modify create new list adding owners, type and bucket id to the entry based on random selection

BUCKET_LIST = list()
for type in BUCKETS:
    type_name = type['type']

    for person in type['people']:
        owner = person['owner']
        num_buckets = random.randint(1,4) # pick a random number of buckets for this person
        bucket_id = 0

        while bucket_id <= num_buckets:
            bucket_uid = hash(owner+str(bucket_id))
            bucket = list()
            num_companies = random.randint(1,10) # pick a random number of companies for this bucket
            random_weights = [random.random() for i in range(0,num_companies)]
            random_company_ids = random.sample(range(500), num_companies)
            weight_sum = sum(random_weights)
            i = 0

            for id in random_company_ids:
                # random_company_ids = random.randint(0,499)
                COMPANIES_LIST[id].update({'owner':owner})
                COMPANIES_LIST[id].update({'type':type_name})
                COMPANIES_LIST[id].update({'bucket_id':bucket_id})
                COMPANIES_LIST[id].update({'unique_bucket_id':bucket_uid})

                if type_name != 'analyst':
                    COMPANIES_LIST[id].update({'weight':random_weights[i]/weight_sum})
                else:
                    COMPANIES_LIST[id].update({'weight':random.randint(0,2)})

                BUCKET_LIST.append(COMPANIES_LIST[id])
                i+=1

            bucket_id+=1

#     To write out new CSV we need to add the fields to the headers
CSV_FIELDS += ['owner','type','bucket_id','unique_bucket_id','weight']

with open(BUCKETS_CSV, 'w') as bucketsfile:
    writer = csv.DictWriter(bucketsfile,CSV_FIELDS)
    writer.writeheader()
    writer.writerows(BUCKET_LIST)