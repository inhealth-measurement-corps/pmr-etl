import csv
import pandas as pd
import math
import pymssql
import time
from datetime import datetime

host = 'INHEALTH.win.ad.jhu.edu'
username = 'WIN\WSE-MeasurementCorps'
password = 'KwGCyTn97nSkFGaFnwP' 
db = 'master'

try:
	# connect to the Microsoft database(not MySQL) use pymssql package other than pymysql
	my_cnxn = pymssql.connect(host=host, user=username, password=password, database=db)
	cursor = my_cnxn.cursor()
except pymssql.Error as e :
    print("Error %d: %s"%(e.args[0],e.args[1]))
    
columns = ['PatientID','BadgeID','Start_Dates','Duration','Distance','Speed','Ambulation','Placehold1','Placehold2','Placehold3','End_Date','Placehold4']
fieldnames = ['PatientID', 'Ambulation', 'Start_Dates', 'Distance', 'Duration', 'Speed']
# reads live.csv
df = pd.read_csv('live.csv', index_col=False, names = columns)

df['Date'] = df.Start_Dates.str[:10]
df['Time of Day'] = df.Start_Dates.str[11:16]
df['Speed'] = df.Speed.round(4)
df = df[['PatientID', 'Ambulation', 'Date', 'Time of Day', 'Distance', 'Duration', 'Speed']]

for index, row in df.iterrows():
	Patient_ID = int(row['PatientID'])
	Ambulation = int(row['Ambulation'])
	Date = datetime.strptime(row['Date'] , '%Y-%m-%d').date()
	Time_of_Day = row['Time of Day']
	Distance = row['Distance']
	Duration = row['Duration']
	Speed = row['Speed']
	dic = (Patient_ID, Ambulation, Date,Time_of_Day, Distance, Duration, Speed)
	sql = """INSERT INTO mmambulation.live_details(patient_ID, ambulation, date,time_of_day,distance, duration, speed)
			VALUES (%d, %d, %s,%s,%s,%s,%s)"""
	cursor.execute(sql,dic)

#commit and close the cursor after changing the database
my_cnxn.commit()
cursor.close()
