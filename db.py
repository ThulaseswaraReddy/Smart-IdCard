
import mysql.connector
connection=mysql.connector.connect(
    host="hayabusa.proxy.rlwy.net",
    port=20927,
    user="root",
    password="IOOvrJIozRKwYOTljpYXOzPJNkiyslYv",
    database="railway"
)
cursor=connection.cursor(dictionary=True)
