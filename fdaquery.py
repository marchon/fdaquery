#!/usr/bin/python

import requests, math

fda_baseurl = "https://api.fda.gov/drug/event.json"
count = 0
limit = 99
MAJOR_DICT = {}

#Function to get all Nuvaring results from openFDA
def getNuvaringBatch(limit, skip):
    params = {"search": "patient.drug.openfda.brand_name:(nuvaring)", \
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


if __name__ == '__main__':

    #Grab the Total Number of Results
    init_results = getNuvaringBatch(limit, 0)
    count = init_results["meta"]['results']['total']
    batches = int(math.ceil(count/limit))

    for batch in range (0,batches):
        print "Processing Batch " + str(batch) + " of " + str(batches)
        results = getNuvaringBatch(limit, batch)
        appendToMajorDict(results["results"], limit, batch)


    print "DONE!"




