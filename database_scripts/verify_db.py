# database_scripts/verify_db.py
import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="Group1",
        password="02062814#afihimz",
        database="agricommerce"
    )
    print("✅ Successfully connected to database!")
    
except mysql.connector.Error as err:
    print(f"❌ Connection failed: {err}")
    
finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()