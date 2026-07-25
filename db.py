
import mysql.connector
connection=mysql.connector.connect(
    host="mysql.railway.internal",
    port=3306,
    user="root",
    password="IOOvrJIozRKwYOTljpYXOzPJNkiyslYv",
    database="railway"
)
cursor=connection.cursor(dictionary=True)
