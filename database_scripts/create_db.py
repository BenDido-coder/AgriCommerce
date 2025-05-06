# database_scripts/create_db.py
import mysql.connector

def create_database():
    try:
        # Connect to MySQL server (not specific database)
        conn = mysql.connector.connect(
            host="localhost",
            user="Group1",
            password="02062814#afihimz"
        )
        
        # Create cursor to execute commands
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS agricommerce")
        print("✅ Database 'agricommerce' created successfully!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_database()