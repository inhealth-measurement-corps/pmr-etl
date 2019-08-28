#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
changed on Aug 16 2019
@author: Ben
"""

import pymssql

# the new DB INFO
host = 'ESMPMMCADBDEV1.win.ad.jhu.edu'
username = 'pmr'
password = 'kQSSD0J9gY4h2hj5OIPp'
db = 'pmr'
# connecting to the microsoft sql database
connection = pymssql.connect(host=host, user=username, password=password, database=db)

try:
    with connection.cursor() as cursor:
        #selects the live data in order to shorten the search for the patient info      
        sql = "SELECT patient_ID FROM live_details"
        cursor.execute(sql)
        result = cursor.fetchall()

        #places all of the ids from the live into a list for easier search
        #also accounts for the duplicates from the list with 
        ids = []
        for i in range(1, len(result)): 
            if result[i - 1] != result[i]: 
                ids.append(result[i - 1])
            if i == (len(result)-1):
                ids.append(result[i])

        #change the tuple list into an array so it can be accessed easier
        newids = []
        for id in ids:
            newids.extend(id)
        #remove the duplicate elements
        newids = list(set(newids))
        
        #determines if there is a discharge date and if so then appends another array with new ids
        changeids = []
        for i in range(len(newids)):
            new = newids[i]
            ql = ("SELECT discharge_date FROM patient_info WHERE patient_ID= %d" %new)
            cursor.execute(ql)
            result1 = cursor.fetchall()
            if result1 != ((None,),):
                changeids.append(new)
                print(new)

        # Create a new record based on the ids that have a discharge date
        for i in range(len(changeids)):
            new = changeids[i]
            cursor.execute("INSERT INTO historical_details (patient_ID, ambulation, date, time_of_day, distance, duration, speed) SELECT patient_ID, ambulation, amb_date, time_of_day, distance, duration, speed FROM live_details WHERE patient_ID = %d;" %new)
            cursor.execute("DELETE FROM live_details WHERE patient_ID = %d;" %new)

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    
finally:
    connection.close()
