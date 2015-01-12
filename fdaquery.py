from __future__ import division
#!/usr/bin/python

import requests, math
from sqlalchemy.orm import sessionmaker
from models import *
import config



fda_baseurl = "https://api.fda.gov/drug/event.json"
count = 0
limit = 99
MAJOR_DICT = {}
DEATH_DICT = {}

#Function to get all Nuvaring results from openFDA
def getNuvaringBatch(limit, skip):
    params = {"search": "patient.drug.openfda.brand_name:(YAZ+OR+Nuvaring)", \
              "limit": limit, \
              "skip": skip}
    r = requests.get(fda_baseurl, params=params)
    results = r.json()
    return results

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

#Function to check if row in table exists.  If so, return the id .. if not, create it and return the id.
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

    for batch in range (0,batches):
        print "Processing Batch " + str(batch + 1) + " of " + str(batches)
        results = getNuvaringBatch(limit, (batch*limit))
        appendToMajorDict(results["results"], limit, batch)

    #deathcount = countDeaths()
    #print "DONE! Nuvaring Deaths = " + str(deathcount)

    #Establish db session
    engine = create_engine(URL(**config.DATABASE))
    Session = sessionmaker(bind=engine)
    session = Session()

    #Iterate through the dict and upload records into postgres database 'fdaquery'

    for event in MAJOR_DICT:

        #Call get_or_create on 'receiver' information:
        if MAJOR_DICT[event]['receiver'] is not None:
            receiverID = get_or_create(session, Receiver, **MAJOR_DICT[event]['receiver'])

        #Call get_or_create on 'sender' information:
        if MAJOR_DICT[event]['sender'] is not None:
            senderID = get_or_create(session, Receiver, **MAJOR_DICT[event]['sender'])
        pass



