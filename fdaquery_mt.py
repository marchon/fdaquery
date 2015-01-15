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

#Function to remove lists of sub-dictionaries out of an existing dictionary - returns a dict
def filter_out_dicts(dict):
    for key in iter(dict.keys()):
        if type(dict[key]) == type([]):
            for item in dict[key]:
                if type(item) == type ({}):
                    dict.pop(key, None)
                    break
        elif type(dict[key]) == type({}):
            dict.pop(key, None)

    return dict

#Function to check if row in table exists.  If so, return the  ... if not, create it and return the id.
def get_or_create(session, model, **kwargs):
    #subdict = filter_out_dicts(kwargs)
    instance = session.query(model).filter_by(**(filter_out_dicts(kwargs))).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

#Function to create record with checking if it exists first.
def create_record(model, session, **kwargs):
    instance = model(**(filter_out_dicts(kwargs)))
    session.add(instance)
    session.commit()
    return instance

#Function to create an entire adverse event from MAJOR_DICT.
def create_adverse_event(event):

    #Create new session
    session = Session()

    #Rename @epoch key
    if MAJOR_DICT[event].has_key('@epoch'):
        MAJOR_DICT[event]['epoch'] = MAJOR_DICT[event].pop('@epoch')

    #Create Event in Event table
    if MAJOR_DICT.has_key(event) and MAJOR_DICT[event] is not None:
        eventOBJ = get_or_create(session, Event, **MAJOR_DICT[event])

        #Call get_or_create on 'receiver' information
        if MAJOR_DICT[event]['receiver'] is not None:
            receiverOBJ = get_or_create(session, Receiver, **MAJOR_DICT[event]['receiver'])
            eventOBJ.receiver=receiverOBJ

        #Call get_or_create on 'sender' information
        if MAJOR_DICT[event]['sender'] is not None:
            senderOBJ = get_or_create(session, Sender, **MAJOR_DICT[event]['sender'])
            eventOBJ.sender=senderOBJ

        #Call get_or_create on 'primarysource' information
        if MAJOR_DICT[event].has_key('primarysource') and MAJOR_DICT[event]['primarysource'] is not None:
            primarysourceOBJ = get_or_create(session, Primarysource, **MAJOR_DICT[event]['primarysource'])
            eventOBJ.primarysource=primarysourceOBJ

        #Call get_or_create on 'reportduplicate' information
        if MAJOR_DICT[event].has_key('reportduplicate') and MAJOR_DICT[event]['reportduplicate'] is not None:
            reportduplicateOBJ = get_or_create(session, Reportduplicate, **MAJOR_DICT[event]['reportduplicate'])
            eventOBJ.reportduplicate=reportduplicateOBJ

        #Call get_or_create on 'patient' information and in turn ... 'drug' and 'reaction'
            if MAJOR_DICT[event]['patient'] is not None:
                patientOBJ = get_or_create(session, Patient, **MAJOR_DICT[event]['patient'])
                eventOBJ.patient=patientOBJ

                #Call get_or_create on 'reaction' information
                if MAJOR_DICT[event]['patient'].has_key('reaction') and MAJOR_DICT[event]['patient']['reaction'] is not None:
                    for reaction in MAJOR_DICT[event]['patient']['reaction']:
                        reactionOBJ = get_or_create(session, Reaction, **reaction)
                        patientOBJ.reaction.append(reactionOBJ)

                #Call get_or_create on 'drug' information
                if MAJOR_DICT[event]['patient'].has_key('drug') and MAJOR_DICT[event]['patient']['drug'] is not None:
                    for drug in MAJOR_DICT[event]['patient']['drug']:
                        drugsOBJ = get_or_create(session, Drugs, **drug)
                        patientOBJ.drugs.append(drugsOBJ)

    #Commit and Tear Down session
    try:
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()




if __name__ == '__main__':

    #Grab the Total Number of Results
    init_results = getNuvaringBatch(limit, 0)
    count = init_results["meta"]['results']['total']
    batches = int(math.ceil(count / limit))

    numThreads = 20
    threads = []

    for batch in range (0, batches):
        #print "Processing Batch " + str(batch + 1) + " of " + str(batches)
        t = threading.Thread(target=getNuvaringBatch_mt, args=(limit, (batch*limit), batch, batches))
        threads.append(t)
        t.start()
        if len(threads) == numThreads:
            for x in threads:
                x.join()

            del threads[:]
    for x in threads:
        x.join()

    #Establish db session
    engine = create_engine(URL(**config.DATABASE))
    Session = sessionmaker(bind=engine)


    #Iterate through the dict and upload records into postgres database 'fdaquery'
    numThreads = 1
    threads = []
    for event in MAJOR_DICT:

        print "Processing Event " + str(event)
        t = threading.Thread(target=create_adverse_event, args=(event,))
        threads.append(t)
        t.start()
        if len(threads) == numThreads:
            for x in threads:
                x.join()

            del threads[:]
    for x in threads:
        x.join()
