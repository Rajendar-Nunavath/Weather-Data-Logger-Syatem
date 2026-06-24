import os
import json
import datetime
import requests
import mysql.connector
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("WEATHER_API_KEY")


def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except mysql.connector.Error as err:
        print(f" Database Connection Error: {err}")
        return None


def init_db():
    """Initializes the database table structure if it doesn't exist."""
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
            raw_response TEXT
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f" Table Initialization Error: {err}")
        return False


def call_weather_api(city):
    """Retrieves current weather details from WeatherAPI for a specific city."""
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": API_KEY,
        "q": city
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            data = response.json()
            if "error" in data:
                print(f" API Error: {data['error']['message']}")
            return None
    except Exception as e:
        print(f" Network/Request Error: {e}")
        return None


def insert_weather_data(conn, data):
    """Parses API response data and persists records into MySQL."""
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
         search_date, search_time, feels_like, pressure, visibility, uv_index, raw_response) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (city_name, country, temperature, humidity, wind_speed, weather_condition,
                  current_date, current_time, feels_like, pressure, visibility, uv_index, raw_response_str)
        
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
        return True
    except mysql.connector.Error as err:
        print(f" Error saving to database: {err}")
        return False


def display_weather_report(data):
    """Prints the clear on-screen visual summary block."""
    print("\n" + "-"*32 + "Weather Report" + "-"*32)
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
    print("-" * 78)


def view_history(conn):
    """Retrieves and cleanly lists comprehensive records stored in MySQL."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, city, temperature, weather_condition, search_date, search_time FROM weather_reports")
        rows = cursor.fetchall()
        
        if not rows:
            print("\n No history records found in database.")
            return

        print(f"\n{'ID':<5} | {'City':<20} | {'Temp':<8} | {'Condition':<20} | {'Date':<12} | {'Time':<10}")
        print("-" * 85)
        for row in rows:
            print(f"{row[0]:<5} | {row[1]:<20} | {row[2]}°C   | {row[3]:<20} | {str(row[4]):<12} | {str(row[5]):<10}")
    except mysql.connector.Error as err:
        print(f" Failed to fetch database logs: {err}")
    finally:
        cursor.close()


def view_last_search(conn):
    """Displays the single most recently recorded search instance."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, city, temperature, weather_condition, search_date, search_time FROM weather_reports ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            print("\n Last Weather Search Record:")
            print(f"ID: {row[0]} | City: {row[1]} | Temp: {row[2]}°C | Condition: {row[3]} | Date: {row[4]} | Time: {row[5]}")
        else:
            print("\n No previous records found.")
    except mysql.connector.Error as err:
        print(f" Error: {err}")
    finally:
        cursor.close()


def display_extreme_city(conn, ordering="DESC"):
    """Identifies and surfaces extreme metric boundaries (Hottest/Coldest)."""
    label = "Hottest" if ordering == "DESC" else "Coldest"
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT city, temperature, weather_condition FROM weather_reports ORDER BY temperature {ordering} LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            print(f"\n {label} City Checked:")
            print(f"City: {row[0]} | Temperature: {row[1]}°C | Condition: {row[2]}")
        else:
            print("\n Database contains no metrics history.")
    except mysql.connector.Error as err:
        print(f" Error sorting data records: {err}")
    finally:
        cursor.close()


def view_search_counter(conn):
    """Outputs absolute structural search row counter counts."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM weather_reports")
        count = cursor.fetchone()[0]
        print(f"\n Total Weather Searches Stored: {count}")
    except mysql.connector.Error as err:
        print(f" Error counting records: {err}")
    finally:
        cursor.close()


def delete_history(conn):
    """Wipes log tracking clean via explicit data deletions."""
    confirm = input("\n Are you sure you want to delete ALL weather history? (yes/no): ").lower()
    if confirm == "yes":
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM weather_reports")
            conn.commit()
            print(" Weather history cleared successfully!")
        except mysql.connector.Error as err:
            print(f" Failed to truncate records: {err}")
        finally:
            cursor.close()
    else:
        print(" Clear operation canceled.")


def export_history(conn):
    """Outputs basic structural values tracking metrics to external TXT files."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT city, temperature, weather_condition FROM weather_reports")
        rows = cursor.fetchall()
        
        if not rows:
            print("\n Nothing to export.")
            return

        with open("weather_history.txt", "w", encoding="utf-8") as file:
            for row in rows:
                file.write(f"{row[0]} | {row[1]}°C | {row[2]}\n")
        
        print(" Weather logs written successfully to 'weather_history.txt'!")
    except (mysql.connector.Error, IOError) as err:
        print(f" File/Data exporting issue occurred: {err}")
    finally:
        cursor.close()


def display_statistics(conn):
    """Runs structural SQL aggregates to show metrics dashboards."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*), 
                MAX(temperature), 
                MIN(temperature), 
                AVG(temperature) 
            FROM weather_reports
        """)
        stats = cursor.fetchone()
        
        if stats and stats[0] > 0:
            print("\n Database Aggregated Statistics")
            print(f" Total Searches       : {stats[0]}")
            print(f" Highest Temperature  : {stats[1]}°C")
            print(f" Lowest Temperature   : {stats[2]}°C")
            print(f" Average Temperature  : {round(stats[3], 2)}°C")
            print("-" * 41)
        else:
            print("\n Insufficient tracking details for statistical aggregations.")
    except mysql.connector.Error as err:
        print(f" Error parsing statistics data: {err}")
    finally:
        cursor.close()


def main_menu():
    """Main lifecycle and workflow handling operations coordination."""
    if not init_db():
        print(" Terminating application due to fatal setup failure.")
        return

    while True:
        print("\n================ WEATHER LOG SYSTEM ================")
        print("1. Check Weather")
        print("2. View Weather History")
        print("3. View Last Weather Search")
        print("4. Hottest City Checked")
        print("5. Coldest City Checked")
        print("6. Weather Search Counter")
        print("7. Delete Weather History")
        print("8. Export Weather History")
        print("9. Statistics Dashboard")
        print("10. Exit")
        print("====================================================")
        
        choice = input("Enter choice (1-10): ").strip()
        
        conn = get_db_connection()
        if not conn:
            print(" Connection error. Re-trying option selection process...")
            continue

        if choice == "1":
            city = input("\nEnter City Name: ").strip()
            if city:
                weather_payload = call_weather_api(city)
                if weather_payload:
                    display_weather_report(weather_payload)
                    insert_weather_data(conn, weather_payload)
            else:
                print(" Input target city value blank.")
                
        elif choice == "2":
            view_history(conn)
        elif choice == "3":
            view_last_search(conn)
        elif choice == "4":
            display_extreme_city(conn, "DESC")
        elif choice == "5":
            display_extreme_city(conn, "ASC")
        elif choice == "6":
            view_search_counter(conn)
        elif choice == "7":
            delete_history(conn)
        elif choice == "8":
            export_history(conn)
        elif choice == "9":
            display_statistics(conn)
        elif choice == "10":
            print("\n Exiting system logging engine. Have a wonderful day!")
            conn.close()
            break
        else:
            print(" Invalid entry option selected. Select numbers 1-10.")
            
        conn.close()


if __name__ == "__main__":
    main_menu()