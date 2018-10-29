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
import datetime
import names
import json

# 'Global' variables

USERS_INPUT_CSV = '../data/Finance/user-prefs.csv'
CLIENTS_CSV = '../data/Finance/clients.csv'
CLIENT_ACCOUNTS_CSV = '../data/Finance/client_accounts.csv'

GENDERS = ['male', 'female']
ACCOUNT_TYPES = ['Roth IRA', 'Roth 401(k)', 'Traditional IRA', 'Brokerage', '529']
ADVISORS_LIST = list()


RANDOM_SEED = 123 # Integer. set to None to make script random on every run (using system time)
random.seed(RANDOM_SEED)

with open(USERS_INPUT_CSV,'r') as users_file:
    companies_reader = csv.DictReader(users_file)

    for row in companies_reader:
        if row["role"] == "advisor":
            ADVISORS_LIST.append(row["username"])


with open('./addresses.json', 'r') as addresses_file:
    s = addresses_file.read().replace('\n', '')
    ADDRESS_LIST = json.loads(s)

num_clients = random.randint(1000,1500)

client_id = 0
account_id = 0

clients_file = open(CLIENTS_CSV, 'w')
clients_file_writer = csv.DictWriter(clients_file, ['first_name', 'last_name', 'full_name', 'client_id', 'dob', 'age', 'inception', 'city', 'state', 'street', 'advisor', 'lat', 'lon'])
clients_file_writer.writeheader()

accounts_file = open(CLIENT_ACCOUNTS_CSV, 'w')
accounts_file_writer = csv.DictWriter(accounts_file, ['status', 'open', 'close', 'type', 'account_id', 'client_id'])
accounts_file_writer.writeheader()

while client_id < num_clients:
    client = dict()
    client_id += 1
    client['client_id'] = client_id
    advisor_s = random.choice(ADVISORS_LIST)
    client['advisor'] = advisor_s
    gender = random.choice(GENDERS)

    # name
    first_name = names.get_first_name(gender)
    last_name = names.get_last_name()
    client['first_name'] = first_name
    client['last_name'] = last_name
    client['full_name'] = first_name + ' ' + last_name

    # location
    address = random.choice(ADDRESS_LIST)
    while 'city' not in address:
        address = random.choice(ADDRESS_LIST)
    client['street'] = address['address1']
    client['city'] = address['city']
    client['state'] = address['state']
    client['lat'] = address['coordinates']['lat']
    client['lon'] = address['coordinates']['lng']

    # DOB / age.  age will get stale over time so this should be rerun periodically
    year = random.randint(1950,1990)
    month = random.randint(1,12)
    day = random.randint(1,28)
    dob = datetime.date(year, month, day)
    age = (datetime.date.today() - dob).days / 365 # not perfect; close enough
    client['dob'] = dob
    client['age'] = age

    # date they became a client
    year = random.randint(2000, 2017)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    inception = datetime.date(year, month, day)
    client['inception'] = inception

    clients_file_writer.writerow(client)

    # accounts
    account_types = random.sample(ACCOUNT_TYPES, random.randint(1, len(ACCOUNT_TYPES)))
    account_idx = 0
    for account_type in account_types:
        account = dict()
        account_id += 1
        account['account_id'] = account_id
        account['client_id'] = client_id

        account['type'] = account_types[account_idx]
        account_idx += 1

        account_open = inception + datetime.timedelta(days = random.randint(20, (datetime.date.today() - inception).days - 100))
        account['open'] = account_open

        if random.uniform(0.0, 1.0) < 0.1:
            account['status'] = 'Inactive'
            account['close'] = account_open + datetime.timedelta(days = random.randint(100, (datetime.date.today() - account_open).days))
        else:
            account['status'] = 'Active'

        accounts_file_writer.writerow(account)

clients_file.close()
accounts_file.close()