combined.py:
Function: transfer patient’s information from Versus Excel Sheet.xls to patient_info table. 
What have I done in this file: 
1, Since we use Microsoft SQL server instead of MySQL, we use pymssql package instead of pymysql package. As a result, I change the connection strings.
2, Since we cannot fill NaN into the sql server. I replace it with None. 
3, We cannot use ‘Replace into’ in the Microsoft SQL server. I use insert and update statement instead. And for security, I make the whole SQL statement to be a transaction.   
