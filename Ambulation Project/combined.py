import pymysql
import csv
import pandas
import time
import os
import re

# DB INFO
# TODO: Figure out formatting for multiple badges for single patient_info
# TODO: Push stuff from excel to database: Starting from 342 = 113, there is a one to one coorespondance (343 = 114, etc).
# Currently does not import patients that have multiple badges. Badge information will be imported as 0s. 
# My suggested solution is to format these into multiple lines, and for any additional badges mark the patient ID with a letter. 
# For example, Patient 500 has badges 1 and 2. Format this as first row having Patient 500 with badge 1, second row as Patient 500b having badge 2. This would also require the SQL table's format for patient ID to be changed from integer to string.

host = "ESMPMMCADBDEV1.win.ad.jhu.edu"
username = "pmr"
password = "kQSSD0J9gY4h2hj5OIPp"
db = "pmr"

my_cnxn = pymysql.connect(host=host, user=username, passwd=password, db=db)
my_cursor = my_cnxn.cursor()

#def insert_records(table, yourcsv, cursor, cnxn):
#    with open(yourcsv) as csvfile:
#        csvFile = csv.reader(csvfile, delimiter=',')
#        header = next(csvFile)
#        headers = map((lambda x: x.strip()), header)
#        insert = 'INSERT INTO {} ('.format(table) + ', '.join(headers) + ') VALUES '
#        for row in csvFile:
#            values = map((lambda x: "'"+x.strip()+"'"), row)
#            b_cursor.execute(insert +'('+ ', '.join(values) +');' )
#            b_cnxn.commit() #must commit, no auto commit

			
#while True: #(for infinite looping)



while True: #(for infinite looping)
	df = pandas.read_excel('Versus Excel Sheet.xlsx', usecols=[0, 1, 17, 6, 15, 16, 18, 20, 23], skiprows=[1])
	#df.reindex(columns=[*df.columns.tolist(), 'col1', 'col2'], fill_value=0)
	df['Unnamed: 8'] = "NULL"
	df['Unnamed: 9'] = "NULL"
	df = df.fillna("NULL")
	df['Versus Data'] = df['Versus Data'].replace(',', '', regex=True)
	df['Unnamed: 1'] = df['Unnamed: 1'].replace(',', '', regex=True)
	df['Unnamed: 2'] = df['Unnamed: 2'].replace(',', '', regex=True)
	df['Unnamed: 3'] = df['Unnamed: 3'].replace(',', '', regex=True)
	df['Unnamed: 4'] = df['Unnamed: 4'].replace(',', '', regex=True)
	df['Unnamed: 5'] = df['Unnamed: 5'].replace(',', '', regex=True)
	df['Unnamed: 6'] = df['Unnamed: 6'].replace(',', '', regex=True)
	df.to_csv('output.csv', encoding='utf-8')
	with open('output.csv') as f:
		with open("temp.csv",'w') as f1:
			reader = csv.reader(f, quotechar = '"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
			for row in reader:
				f1.write(",".join([re.sub("\D", "", row[8]),row[1],row[5],row[2],row[3],row[4],row[6],row[7],row[9],row[10],row[8]]))
				f1.write('\n')
	with open("temp.csv",'r') as f:
		with open("output.csv",'w') as f1:
			f.readline() # skip header line
			for line in f:
				f1.write(line)
	os.remove("temp.csv")
	print('Loop finished')
	csv_data = csv.reader(open('output.csv'))
	for row in csv_data:
		my_cursor.execute("REPLACE INTO patient_info VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row[:11])
	#my_cursor.close()
