import pandas as pd
import openpyxl
from csv import reader
import pymssql
import time
from datetime import datetime
from time import strptime
from openpyxl import load_workbook

import math 
 
# the new DB INFO
host = 'INHEALTH.win.ad.jhu.edu'
username = 'WIN\WSE-MeasurementCorps'
password = 'KwGCyTn97nSkFGaFnwP' 
db = 'master'
# connecting to the microsoft sql database
connection = pymssql.connect(host=host, user=username, password=password, database=db)




#get the preexisting patient IDs from the patient_info database table 
try:
    with connection.cursor() as cursor:
        sql = "SELECT patient_ID FROM mmambulation.patient_info"

        cursor.execute(sql)
        result = cursor.fetchall()

        #list of existing patient IDs in the patient_info database 
        sqlIDs = []
        for i in range(0, len(result) - 1):
            sqlIDs.append("".join(result[i]))


    with connection.cursor() as cursor2:
        sql2 = "SELECT badge_ID FROM mmambulation.patient_info"

        cursor2.execute(sql2)
        result2 = cursor2.fetchall()
            
        #list of existing badge IDs in the patient_info database 
        sqlBadgeIDs = []
        for i in range(0, len(result) - 1):
            sqlBadgeIDs.append("".join(result[i]))
            
except:
    print("Error with connecting to database")

#get the patient IDs from the excel sheet from the shared network table 
excelIDs = [] 
shared_file = "S:\BrownActigraphyLogs\Versus excel sheet_01_07_2020.xlsx"
df = pd.read_excel(shared_file)
df.to_csv('versus.csv', index=False)

book = load_workbook("S:\BrownActigraphyLogs\Versus excel sheet_01_07_2020.xlsx")
sheet = book['Sheet1']
 
                
try:
    with connection.cursor() as cursor3:
        for row in sheet.rows:
            if (str(row[0].value).isdigit()):
                patientID = str(row[0].value)[0:3]
                new = int(patientID)
                
                #the patient is in the current database
                if (patientID in sqlIDs):
                    #get index of patient ID in sqlIDs
                    #see if the badgeID was updated
                    if (str(row[1].value).isdigit()): 
                        badgeID = int(row[1].value)
                        index = sqlIDs.index(patientID)
                        if(badgeID != sqlBadgeIDs[index]):
                            badgeID = badgeID
                           # q3 = ('''UPDATE mmambulation.patient_info SET badge_ID = %d WHERE patient_ID= %d;''' %(badgeID, new))
                           # cursor3.execute(q3)
                    #see if a dischargeDate was added, if so update the discharge date                      
                    if (row[18].value != None):
                         if (isinstance(row[18].value, datetime)):
                             dischargeDate = row[18].value
                             q3 = ("SELECT discharge_date FROM mmambulation.patient_info WHERE patient_ID= %d" %new)
                             cursor3.execute(q3)

                             result3 = cursor3.fetchall();
                             for i in result3:
                                 if (str(i) == '(None,)'):
                                     new = new 
                                     #q3 = ('''UPDATE mmambulation.patient_info SET discharge_date = %d WHERE patient_ID= %d;''' %(discharge_date, new))
                                     #cursor3.execute(q3)
                                     #connection.commit() 
               

                #the patient is not in the current database 
                else:
                    if (str(row[1].value).isdigit()): 
                        badgeID = (row[1].value)
                    else:
                        badgeID = None 
                    roomNumber = row[17].value
                    if (str(row[6].value) != 'None'):
                        admissionDate = str(row[6].value)[0:10]
                    #transferDate = (row[24].value)
                    #transferTime = (row[25].value)
                    if (str(row[18].value) != 'None'):
                        dischargeDate = str(row[18].value)[0:10]
                    if (str(row[20].value).isdigit()): 
                        lengthOfStay = int(row[20].value)
                    else:
                        lengthOfStay = 0;

                    #q3 = ("INSERT INTO mmambulation.patient_info VALUES (%d, %d, %d, %s, %s, %s, %s, %d);", %(patientID, badgeID, roomNumber, admissionDate, transferDate, transferTime, dischargeDate, 384, 'Null', 'Null');")
                    #cursor.execute(q3)


                          

                connection.commit() 
except:
    print("Error with editing database")




