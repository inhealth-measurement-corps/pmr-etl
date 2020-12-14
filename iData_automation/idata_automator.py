import os.path, time
import pymssql
import csv
import os
import mmap

host = 'INHEALTH.win.ad.jhu.edu'
username = 'WIN\WSE-MeasurementCorps'
password = 'KwGCyTn97nSkFGaFnwP' 
db = 'master'

file1 = open("test_record.txt", "a+")
file1.write("Test Record \n") 
file1.close()

file2 = open("removed_patients_record.txt", "a+")
file2.write("Removed Patients Record \n") 
file2.close()

file3 = open("IData.csv", "w")
writer = csv.writer(file3)
file3.close()
# this automator's function is to transfer data from database(patient_info table) to IData.csv
# test_record -> the patients who is still in the hospital
# removed_patients_record -> the patients who have been discharged
# iData -> the patients who has not been discharged(still in the hospital)

# connecting to the sql server database
my_cnxn = pymssql.connect(host=host, user=username, password=password, database=db)
# make a cursor object that lets us navigate through the database
cur = my_cnxn.cursor()

while True: #continuous loop
    # get the patient_info table
    cur.execute("SELECT * FROM mmambulation.live_details")
    # parameter '+a' means open a file for reading and writing
    # mmap's goal: Use a memory mapped file instead of reading the content directly.
    # fileno() is the file descriptor, parameter '0' means mapping the entire file, ACCESS_READ means read only
    file1 = open("test_record.txt","a+")
    s1 = mmap.mmap(file1.fileno(), 0, access = mmap.ACCESS_READ)

    file2 = open("removed_patients_record.txt","a+")
    s2 = mmap.mmap(file2.fileno(), 0, access = mmap.ACCESS_READ)

    live_p = [] 
    for row in cur.fetchall():
        live_p.append(row[0])

    for i in range(len(live_p)):
        new = live_p[i]
        ql = ("SELECT * FROM mmambulation.patient_info WHERE patient_ID= %d" %new)
        cur.execute(ql)
        result1 = cur.fetchall()
        for row in result1: 
            identifier = str(row[0]) + ',' + str(row[1]) + ',' +str(row[2])
            date_and_time = str(row[3])
            discharge_date = str(row[6])
            found_value_1 = s1.find(str.encode(identifier)) #is greater than -1 if the identifier exists in the file
            print("The found value for patient " + str(row[0]) + " is " + str(found_value_1))

            if found_value_1 == -1 and discharge_date == 'None': #This is a new entry in the patient info table and they haven't been discharged yet
                print("Patient " + str(row[0]) + " is a new entry.")
                #we want to take the data and append it to a idata.csv file

                line_ender = "N/A</br>" # thing we need to end the line with

                insert_row = [row[0], row[1], date_and_time, line_ender]
                #with open('IData.csv', 'a',encoding='utf-8') as csvFile:
                with open('IData.csv', 'a') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(insert_row)

                # add the id and date thing to the txt file
                file1.write(identifier + '\n')

            found_value_2 = s2.find(str.encode(identifier)) #is greater than -1 if the identifier exists in the file

            if discharge_date != 'None' and found_value_2 == -1: #patient has been discharged, they haven't been removed from IData.csv yet and should be
                print ("Patient " + str(row[0]) + " was discharged.")
                discharged_identifier = str(row[0]) 
                lines = list()
                with open('IData.csv', 'r') as csvFile:
                    reader = csv.reader(csvFile)
                    for row in reader:
                        if discharged_identifier != row[0]:
                            lines.append(row)

                with open('IData.csv', 'w') as writeFile:
                    writer = csv.writer(writeFile)
                    writer.writerows(lines)

                file2.write(identifier + '\n') # add this discharged patient into the removed_patients_record

    file1.close()
    file2.close()
    print("ending loop")
    time.sleep(10) #Make it loop every mintue
    print(" ")

