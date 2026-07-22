import mysql.connector
connection=mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_MYSQL_PASSWORD",
    database="SmartIdCard"
)
cursor=connection.cursor(dictionary=True)