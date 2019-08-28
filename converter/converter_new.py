#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
changed on Aug 16 2019
@author: Ben
"""
import pymssql
from conv_classes import Patient, Ambulation
import numpy as np
import csv
from datetime import datetime

# the new DB INFO
host = 'ESMPMMCADBDEV1.win.ad.jhu.edu'
username = 'pmr'
password = 'kQSSD0J9gY4h2hj5OIPp'
db = 'pmr'

# connecting to the microsoft sql database
db = pymssql.connect(host=host, user=username, password=password, database=db)
cur = db.cursor() #make a cursor object that lets us navigate through the database
cur2 = db.cursor() #make a second cursor to go through the patient_info table
cur.execute("SELECT * FROM historical_details") #get the ambulation table

patient_map = {} # A map of patient numbers/MRNs to patient objects

for row in cur.fetchall():
    if patient_map.get(row[0]) != None: #if the patient is already in our dict
        patient = patient_map[row[0]] #get the patient object corresponding to this MRN - stays the same

        start_date = datetime.strptime(row[2], '%Y-%m-%d').date()
        #start_time = datetime.strptime(row[3][:-8], "%H:%M:%S").time()
        ambulation = Ambulation(row[0], start_date, row[3], row[4], row[5], row[6], row[1])
        patient.add_ambulation(ambulation)

    else: #the patient is not in our dict yet
        cur2.execute("SELECT * FROM patient_info WHERE patient_ID = %s", (row[0],))
        row2 = cur2.fetchone()
        admission_date = datetime.strptime(row2[2], '%Y-%m-%d').date()
        transfer_date = datetime.strptime(row2[3], '%Y-%m-%d').date()
        discharge_date = datetime.strptime(row2[4], '%Y-%m-%d').date()
        patient = Patient(row[0], row2[1], row2[7], admission_date, transfer_date, discharge_date, row2[5])

        start_date = datetime.strptime(row[2], '%Y-%m-%d').date()
        ambulation = Ambulation(row[0], start_date, row[3], row[4], row[5], row[6], row[1])
        patient.add_ambulation(ambulation)
        patient_map[patient.mrn] = patient


#Need to do regression on each patient to get deltas
for x, y in patient_map.items():
    #print()
    #print("Data for MRN", x)
    y.regression_v3()
    y.print_data()

for x, y in patient_map.items():
    print(y.date_to_day)

with open("Ambulation_Unit.csv", 'a', newline='') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(["Patient ID", "# of Ambulations (N)", "Ambulation Frequency (N/LoS)", "Days with ambulation (number)", "Compliance 1/day (%)", "Compliance 2/day (%)", "Compliance 3/day (%)", "Total Distance (ft)", "Distance CoT","Duration CoT","Speed CoT"])
    for x, y in patient_map.items():
        freq = y.num_ambulations/y.length_of_stay
        filewriter.writerow([y.mrn, y.num_ambulations, freq, len(y.ambulations_per_day), y.compliance_1, y.compliance_2, y.compliance_3, y.total_distance, y.delta_dist, y.delta_dur, y.delta_speed])

with open("Ambulation_Daily.csv", 'a',newline='') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(["Patient ID", "Day on Unit", "# of Ambulations", "Dist Max", "Dist Mean", "Dist Min", "Dur Max", "Dur Mean", "Dur Min","Speed Max","Speed Mean", "Speed Min"])
    for x, y in patient_map.items():
        for a, b in y.date_to_day.items():
            filewriter.writerow([y.mrn, b.day_number, b.num_ambulations, b.max_dist, b.mean_dist, b.min_dist, b.max_dur ,b.mean_dur, b.min_dur, b.max_speed, b.mean_speed, b.min_speed])

cur.close()
cur2.close()

