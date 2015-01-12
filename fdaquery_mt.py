from __future__ import division
#!/usr/bin/python

import requests, math, threading
from sqlalchemy.orm import sessionmaker
from models import *
import config



fda_baseurl = "https://api.fda.gov/drug/event.json"
count = 0
limit = 99
MAJOR_DICT = {}
DEATH_DICT = {}

#Function to get all Nuvaring results from openFDA
def getNuvaringBatch_mt(limit, skip, batch, batches):
    params = {"search": "patient.drug.openfda.brand_name:(YAZ+OR+Nuvaring)", \
              "limit": limit, \
              "skip": skip}
    r = requests.get(fda_baseurl, params=params)
    results = r.json()

    appendToMajorDict(results['results'], limit, batch)
    print "Processing Batch " + str(batch + 1) + " of " + str(batches)

def getNuvaringBatch(limit, skip):
    params = {"search": "patient.drug.openfda.brand_name:(YAZ+OR+Nuvaring)", \
              "limit": limit, \
              "skip": skip}
    r = requests.get(fda_baseurl, params=params)
    results = r.json()
    return results

    #appendToMajorDict(results['results'], limit, batch)
    #print "Processing Batch " + str(batch + 1) + " of " + str(batches)

#Function to re-enumerate the id's and populate a master dictionary based on the batch limit of openFDA
def appendToMajorDict(dict, limit, batch):
    index = 0
    for result in dict:
        id = index + (limit * batch)
        MAJOR_DICT[id] = result
        index += 1

#Function to count deaths
def countDeaths():
    deathcount = 0
    for dict in MAJOR_DICT:
        if MAJOR_DICT[dict].has_key("seriousnessdeath"):
            deathcount += 1
            DEATH_DICT[dict] = MAJOR_DICT[dict]
    return deathcount

#Function to check if row in table exists.  If so, return the  ... if not, create it and return the id.
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance.id
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance.id



if __name__ == '__main__':

    #Grab the Total Number of Results
    init_results = getNuvaringBatch(limit, 0)
    count = init_results["meta"]['results']['total']
    batches = int(math.ceil(count / limit))

    numThreads = 15
    threads = []

    for batch in range (0, batches):
        #print "Processing Batch " + str(batch + 1) + " of " + str(batches)
        t = threading.Thread(target=getNuvaringBatch_mt, args=(limit, (batch*limit), batch, batches))
        threads.append(t)
        if len(threads) == numThreads:
            for x in threads:
                x.start()

            for x in threads:
                x.join()

            del threads[:]

    #Establish db session
    engine = create_engine(URL(**config.DATABASE))
    Session = sessionmaker(bind=engine)
    session = Session()

    #Iterate through the dict and upload records into postgres database 'fdaquery'

    for event in MAJOR_DICT:

        print "Processing Event " + str(event)
        #Call get_or_create on 'receiver' information
        if MAJOR_DICT[event]['receiver'] is not None:
            receiverID = get_or_create(session, Receiver, **MAJOR_DICT[event]['receiver'])

        #Call get_or_create on 'receiver' information
        if MAJOR_DICT[event]['sender'] is not None:
            senderID = get_or_create(session, Sender, **MAJOR_DICT[event]['sender'])





