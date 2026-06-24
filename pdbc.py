import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    print("✅ Database Connected Successfully!")

    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    print("Current Database:", cursor.fetchone()[0])
    # sql = "INSERT INTO std1 (id,username, email) VALUES (%s,%s, %s)"

    # Values to insert
    # values = (3,"Rajesh", "rajesh@gmail.com")

    # cursor.execute(sql, values)

    # Save changes
    # conn.commit()

    # print("✅ Record inserted successfully!")
    # print("Inserted ID:", cursor.lastrowid)

    # cursor.execute("SELECT * FROM std1")
    # rows = cursor.fetchall()

    # print(rows)
    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())

    cursor.execute("SELECT COUNT(*) FROM std1")
    print(cursor.fetchone())

    cursor.close()
    
    conn.close()

except Exception as e:
    print("❌ Error:", e)