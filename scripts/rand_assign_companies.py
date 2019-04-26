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
import copy

# 'Global' variables

COMPANY_INPUT_CSV = '../data/Finance/sp500.csv'
BUCKETS_CSV = '../data/Finance/company_buckets.csv'

CSV_FIELDS = []

BUCKETS = [
    {'type':'analyst','people':[
        'frank',
        'geoffrey',
        'carla',
        'sophie'
    ]},
    {'type':'advisor','people':[
        'robert',
        'cynthia'
    ]},
    {'type':'manager','people':[
        'lawson',
        'chloe'
    ]}
]

CAPITALIZATIONS = ['Large Cap', 'All Cap', 'Mid Cap', 'Mid and Large Cap']
STRATEGIES = ['Value', 'Blended', '130/30', 'Growth', 'Mixed', 'Domestic']

COMPANIES_LIST = list()

RANDOM_SEED = 123 # Integer. set to None to make script random on every run (using system time)
random.seed(RANDOM_SEED)

# global ANALYSTS, CLIENTS, MANAGERS, COMPANIES_DICT # access global variables for modification

# Easiest way is just to read company CSV into list since it is small
with open(COMPANY_INPUT_CSV,'r') as companiesfile:
    companies_reader = csv.DictReader(companiesfile,restkey="state")
    CSV_FIELDS = companies_reader.fieldnames

    for company_dict in companies_reader:
        COMPANIES_LIST.append(company_dict)

# Modify create new list adding owners, type and bucket id to the entry based on random selection

BUCKET_LIST = list()
for type in BUCKETS:
    type_name = type['type']

    for owner in type['people']:
        if type_name != 'analyst':
            num_buckets = random.randint(1,4) # pick a random number of buckets for this person
        else:
            num_buckets = 2 # analysts have their covered companies, and companies they follow

        bucket_id = 0

        while bucket_id < num_buckets:


            bucket_uid = hash(owner+str(bucket_id))
            bucket = list()
            if type_name == 'analyst':
                num_companies = random.randint(8,10)
            else:
                num_companies = random.randint(12,18)
            random_weights = [random.random() for c in range(0,num_companies)] # generate some random weights
            random_company_ids = random.sample(range(500), num_companies) # take a random sample from company ids (0-499)
            weight_sum = sum(random_weights)
            weights_id = 0

            for id in random_company_ids:
                temp = copy.deepcopy(COMPANIES_LIST[id])
                temp.update({'owner':owner})
                temp.update({'type':type_name})
                temp.update({'bucket_id':bucket_id})
                temp.update({'unique_bucket_id':bucket_uid})
                if type_name != 'analyst':
                    bucket_value_total = random.randint(100000000.0, 1000000000.0)
                    bucket_name = random.choice(CAPITALIZATIONS) + ' ' + random.choice(STRATEGIES) + ' Strategy'
                    bucket_ytd_ror = random.uniform(0.5, 8.0)
                    bucket_total_clients = random.randint(1000, 2000)
                    temp.update({'weight':random_weights[weights_id]/weight_sum})
                    temp.update({'bucket_value': bucket_value_total * random_weights[weights_id] / weight_sum})
                    temp.update({'bucket_value_total': bucket_value_total})
                    temp.update({'bucket_name': bucket_name})
                    temp.update({'bucket_ytd_ror': bucket_ytd_ror})
                    temp.update({'bucket_total_clients': bucket_total_clients})
                else:
                    if bucket_id == 0:
                        bucket_name = 'Covered Companies'
                        temp.update({'weight': 2})
                    elif bucket_id == 1:
                        bucket_name = 'Followed Companies'
                        temp.update({'weight': 1})
                    else:
                        print 'unexpected bucket_id for analyst'
                        exit(1)
                    temp.update({'bucket_name': bucket_name})
                BUCKET_LIST.append(temp)
                weights_id+=1

            bucket_id+=1

#     To write out new CSV we need to add the fields to the headers
CSV_FIELDS += ['owner','type','bucket_id','unique_bucket_id','weight','bucket_value','bucket_value_total','bucket_name','bucket_ytd_ror','bucket_total_clients']
with open(BUCKETS_CSV, 'w') as bucketsfile:
    writer = csv.DictWriter(bucketsfile,CSV_FIELDS)
    writer.writeheader()
    writer.writerows(BUCKET_LIST)
