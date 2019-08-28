act2hist.py
Function: transfer patients’ data from live_details table to historical_details table. Just update the patients’ data.  
What have I done in this file: 
1, Change the connection string to connect to the new SQL server. 
2, Update patients’ data successfully. 

converter.py
Function: Based on historical_details and patient_info table, get ambulation_unit and ambulation_daily data. 
What have I done in this file: 
1, Change the connection string to connect to the new SQL server. 
2, Make it running and get ambulation_unit.csv and ambulation_daily.csv successfully. 

Problem: since the patient_ID in the patient_info and historical_details is not corresponding, the data we got is wrong.

