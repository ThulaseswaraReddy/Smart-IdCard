import os
import mysql.connector

# Reads cloud environment variables when deployed, or uses your local credentials as fallback
connection = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    port=int(os.environ.get("DB_PORT", 3306)),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", "6264"),
    database=os.environ.get("DB_NAME", "smartidcard"),
    ssl_disabled=(os.environ.get("DB_HOST") is None)
)

cursor = connection.cursor(dictionary=True)




# import mysql.connector
# connection=mysql.connector.connect(
#     host="localhost",
#     port=3306,
#     user="root",
#     password="6264",
#     database="smartidcard"
# )
# cursor=connection.cursor(dictionary=True)
