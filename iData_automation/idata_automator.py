import os.path, time
import pymssql
import csv
import os
import mmap

host = "ESMPMMCADBDEV1.win.ad.jhu.edu"
username = "pmr"
password = "kQSSD0J9gY4h2hj5OIPp"
db = "pmr"
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
    cur.execute("SELECT * FROM patient_info")
    # parameter '+a' means open a file for reading and writing
    # mmap's goal: Use a memory mapped file instead of reading the content directly.
    # fileno() is the file descriptor, parameter '0' means mapping the entire file, ACCESS_READ means read only
    file1 = open("test_record.txt","a+")
    s1 = mmap.mmap(file1.fileno(), 0, access = mmap.ACCESS_READ)

    file2 = open("removed_patients_record.txt","a+")
    s2 = mmap.mmap(file2.fileno(), 0, access = mmap.ACCESS_READ)

    for row in cur.fetchall():
        #identifier combo of patient ID, room_number and admission date
        identifier = str(row[0]) + ',' + str(row[1]) + ',' +str(row[2])

        date_and_time = str(row[3])

        discharge_date = str(row[4])

        found_value_1 = s1.find(str.encode(identifier)) #is greater than -1 if the identifier exists in the file
        print("The found value for patient " + str(row[0]) + " is " + str(found_value_1))

        if found_value_1 == -1 and discharge_date == None: #This is a new entry in the patient info table and they haven't been discharged yet
            print("Patient " + str(row[0]) + " is a new entry.")
            #we want to take the data and append it to a idata.csv file

            line_ender = "N/A</br>" # thing we need to end the line with

            insert_row = [row[0], row[1], date_and_time, line_ender]
            with open('IData.csv', 'a',encoding='utf-8') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(insert_row)

            # add the id and date thing to the txt file
            file1.write(identifier + '\n') 

        found_value_2 = s2.find(str.encode(identifier)) #is greater than -1 if the identifier exists in the file

        if discharge_date != None and found_value_2 == -1: #patient has been discharged, they haven't been removed from IData.csv yet and should be
            print("patient " + str(row[0]) + " has been discharged")
            with open("IData.csv", "r") as f:
                lines = f.readlines()
            with open("IData.csv", "w") as f:
                for line in lines:
                    csf_row_string = str(row[0]) + "," +  str(row[1]) + ","  + date_and_time
                    if line.strip("\n") != csf_row_string:
                        f.write(line)
                    else:
                        print("didn't write a line.")
            file2.write(identifier + '\n') # add this discharged patient into the removed_patients_record
        # print(type(str(ambulation.start_datetime)))

    file1.close()
    file2.close()
    print("ending loop")
    time.sleep(60) #Make it loop every mintue
    print(" ")