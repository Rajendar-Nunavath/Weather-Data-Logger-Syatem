import os
import json
import datetime
import requests
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None


def init_db():
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            country VARCHAR(100),
            temperature DECIMAL(5,2),
            humidity INT,
            wind_speed DECIMAL(5,2),
            weather_condition VARCHAR(100),
            search_date DATE,
            search_time TIME,
            feels_like DECIMAL(5,2),
            pressure DECIMAL(7,2),
            visibility DECIMAL(5,2),
            uv_index DECIMAL(4,1),
            raw_response TEXT,
            validation_status VARCHAR(20) DEFAULT 'VALID'
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Table Initialization Error: {err}")
        return False


def validate_city_input(city_name):
    clean_name = city_name.strip().lower()
    
    if not clean_name or len(clean_name) < 2:
        return False, "Input too short or empty"
        
    allowed_chars = set("abcdefghijklmnopqrstuvwxyz.- ")
    if not set(clean_name).issubset(allowed_chars):
        return False, "City contains unsupported characters"
        
    return True, "VALID"


def call_weather_api(city):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": API_KEY,
        "q": city
    }
    
    try:
        response = requests.get(url, params=params)
        return response.status_code, response.json()
    except Exception as e:
        print(f"Network Error: {e}")
        return 500, {"error": {"message": str(e)}}


def log_invalid_search(conn, city_name, reason_message):
    try:
        cursor = conn.cursor()
        current_date = datetime.date.today()
        current_time = datetime.datetime.now().time().strftime("%H:%M:%S")
        raw_error_payload = json.dumps({"validation_failure_reason": reason_message})

        insert_query = """
        INSERT INTO weather_reports 
        (city, search_date, search_time, raw_response, validation_status) 
        VALUES (%s, %s, %s, %s, 'INVALID')
        """
        values = (city_name, current_date, current_time, raw_error_payload)
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error logging invalid attempt: {err}")


def insert_weather_data(conn, data):
    try:
        cursor = conn.cursor()
        
        city_name = data["location"]["name"]
        country = data["location"]["country"]
        temperature = data["current"]["temp_c"]
        humidity = data["current"]["humidity"]
        wind_speed = data["current"]["wind_kph"]
        weather_condition = data["current"]["condition"]["text"]
        
        current_date = datetime.date.today()
        current_time = datetime.datetime.now().time().strftime("%H:%M:%S")
        
        feels_like = data["current"].get("feelslike_c")
        pressure = data["current"].get("pressure_mb")
        visibility = data["current"].get("vis_km")
        uv_index = data["current"].get("uv")
        
        raw_response_str = json.dumps(data)

        insert_query = """
        INSERT INTO weather_reports 
        (city, country, temperature, humidity, wind_speed, weather_condition, 
         search_date, search_time, feels_like, pressure, visibility, uv_index, raw_response, validation_status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'VALID')
        """
        
        values = (city_name, country, temperature, humidity, wind_speed, weather_condition,
                  current_date, current_time, feels_like, pressure, visibility, uv_index, raw_response_str)
        
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error saving to database: {err}")
        return False


def display_weather_report(data):
    print("\n------------------------- Weather Report -------------------------")
    print(f" City        : {data['location']['name']}")
    print(f" Country     : {data['location']['country']}")
    print(f" Temperature : {data['current']['temp_c']}°C")
    print(f" Feels Like  : {data['current'].get('feelslike_c')}°C")
    print(f" Humidity    : {data['current']['humidity']}%")
    print(f" Wind Speed  : {data['current']['wind_kph']} km/h")
    print(f" Condition   : {data['current']['condition']['text']}")
    print(f" Pressure    : {data['current'].get('pressure_mb')} mb")
    print(f" Visibility  : {data['current'].get('vis_km')} km")
    print(f" UV Index    : {data['current'].get('uv')}")
    print("------------------------------------------------------------------")


def view_history(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, city, temperature, weather_condition, validation_status FROM weather_reports")
        rows = cursor.fetchall()
        
        if not rows:
            print("\nNo history records found.")
            return

        print(f"\n{'ID':<5} | {'City':<20} | {'Temp':<8} | {'Condition':<20} | {'Status':<10}")
        print("-" * 72)
        for row in rows:
            temp_str = f"{row[2]}°C" if row[2] is not None else "N/A"
            cond_str = row[3] if row[3] else "N/A"
            print(f"{row[0]:<5} | {row[1]:<20} | {temp_str:<8} | {cond_str:<20} | {row[4]:<10}")
    except mysql.connector.Error as err:
        print(f"Failed to fetch history: {err}")
    finally:
        cursor.close()


def export_history(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT city, temperature, weather_condition FROM weather_reports WHERE validation_status = 'VALID'")
        rows = cursor.fetchall()
        
        if not rows:
            print("\nNo valid records to export.")
            return

        with open("weather_history.txt", "w", encoding="utf-8") as file:
            for row in rows:
                file.write(f"{row[0]} | {row[1]}°C | {row[2]}\n")
        
        print("Weather history exported to 'weather_history.txt'")
    except (mysql.connector.Error, IOError) as err:
        print(f"Export Error: {err}")
    finally:
        cursor.close()


def export_invalid_history(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT city, search_date, search_time, raw_response FROM weather_reports WHERE validation_status = 'INVALID'")
        rows = cursor.fetchall()
        
        if not rows:
            print("\nNo invalid records to export.")
            return

        with open("invalid_weather_records.txt", "w", encoding="utf-8") as file:
            file.write("City Attempted | Date | Time | Error Detail\n")
            file.write("-" * 60 + "\n")
            for row in rows:
                try:
                    reason_dict = json.loads(row[3])
                    reason = reason_dict.get("validation_failure_reason", "Unknown API error")
                except Exception:
                    reason = "Malformed log string"
                    
                file.write(f"{row[0]} | {row[1]} | {row[2]} | Reason: {reason}\n")
        
        print("Invalid records exported to 'invalid_weather_records.txt'")
    except (mysql.connector.Error, IOError) as err:
        print(f"Export Error: {err}")
    finally:
        cursor.close()


def delete_history(conn):
    confirm = input("\nAre you sure you want to delete ALL history? (yes/no): ").lower()
    if confirm == "yes":
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM weather_reports")
            conn.commit()
            print("Weather history cleared successfully.")
        except mysql.connector.Error as err:
            print(f"Delete Failed: {err}")
        finally:
            cursor.close()
    else:
        print("Operation canceled.")


def display_statistics(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*), 
                MAX(temperature), 
                MIN(temperature), 
                AVG(temperature) 
            FROM weather_reports
            WHERE validation_status = 'VALID'
        """)
        stats = cursor.fetchone()
        
        if stats and stats[0] > 0:
            print("\n--- Weather Statistics (Valid Searches) ---")
            print(f" Total Searches       : {stats[0]}")
            print(f" Highest Temperature  : {stats[1]}°C")
            print(f" Lowest Temperature   : {stats[2]}°C")
            print(f" Average Temperature  : {round(stats[3], 2)}°C")
            print("------------------------------------------")
        else:
            print("\nNo statistical data available.")
    except mysql.connector.Error as err:
        print(f"Statistics Error: {err}")
    finally:
        cursor.close()


def main_menu():
    if not init_db():
        print("Application failure: Database initialization failed.")
        return

    while True:
        print("\n=== WEATHER DATA LOG SYSTEM ===")
        print("1. Check Weather")
        print("2. View History")
        print("3. View Statistics Dashboard")
        print("4. Export Valid History (.txt)")
        print("5. Export Invalid History (.txt)")
        print("6. Clear All History")
        print("7. Exit")
        print("===============================")
        
        choice = input("Enter choice (1-7): ").strip()
        
        conn = get_db_connection()
        if not conn:
            print("Connection error. Retrying...")
            continue

        if choice == "1":
            city = input("\nEnter City Name: ").strip()
            
            is_valid, validation_msg = validate_city_input(city)
            if not is_valid:
                print(f"Validation Error: {validation_msg}")
                log_invalid_search(conn, city, validation_msg)
                conn.close()
                continue
            
            status_code, response_data = call_weather_api(city)
            if status_code == 200:
                display_weather_report(response_data)
                insert_weather_data(conn, response_data)
            else:
                api_error_msg = response_data.get("error", {}).get("message", "Unknown error")
                print(f"API Error: {api_error_msg}")
                log_invalid_search(conn, city, api_error_msg)
                
        elif choice == "2":
            view_history(conn)
        elif choice == "3":
            display_statistics(conn)
        elif choice == "4":
            export_history(conn)
        elif choice == "5":
            export_invalid_history(conn)
        elif choice == "6":
            delete_history(conn)
        elif choice == "7":
            print("\nExiting program.")
            conn.close()
            break
        else:
            print("Invalid selection. Choose 1-7.")
            
        conn.close()


if __name__ == "__main__":
    main_menu()
