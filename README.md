# Weather-Data-Logger-Syatem
Python CLI app fetches live weather via API and logs metrics to MySQL using PDBC. Tracks history , saves raw JSON , exports to TXT , and provides SQL analytics. Mirrors real-world data pipelines.

## 🚀 Key Features

* [cite_start]**Live Weather Retrieval**: Programmatically interfaces with WeatherAPI to grab immediate, live conditions (temperature, humidity, wind speed, condition) for any user-specified city[cite: 95].
* [cite_start]**Automated Historical Logging**: Automatically maps and archives every weather query alongside detailed user-search date and time stamps[cite: 78, 138].
* [cite_start]**Extended Metrics & Payload Auditing**: Captures granular bonus metrics like "Feels Like" index, barometric pressure, UV Index, and preserves the unparsed `raw_response` JSON text for logging integrity[cite: 187, 193].
* [cite_start]**SQL Aggregations & Analytics**: Leverages advanced database logic to deliver instant calculations regarding query counts and historical temperature extrema (Hottest/Coldest cities checked)[cite: 155, 161, 201].
* [cite_start]**Administrative Utilities**: Features robust internal utility paths allowing administrators to smoothly export database history to physical flat-text files (`weather_history.txt`) or selectively clear the log table[cite: 171, 178].

---

## 🛠️ Tech Stack

* [cite_start]**Programming Language**: Python 3.x [cite: 3]
* [cite_start]**Database Management System**: MySQL [cite: 8]
* [cite_start]**API Ingestion Engine**: WeatherAPI Platform [cite: 14]
* **Core Python Modules**: 
  * [cite_start]`requests` (HTTP GET operations and response status checks) [cite: 5, 69]
  * [cite_start]`mysql-connector-python` (Database Driver Connectivity) [cite: 37]
  * [cite_start]`json` (Payload extraction and serialization) [cite: 6]
  * `python-dotenv` (Decoupled environment configuration security)
  * [cite_start]`datetime` (Precise capture of transactional metadata) [cite: 144]

---

## 📦 How to Install & Run

Follow these step-by-step instructions to get your local environment configured and operational:

### 1. Prerequisite Packages
Install the required network and database communication packages using `pip`:
```bash
pip install requests mysql-connector-python python-dotenv
2. Database InitializationLaunch your MySQL server instance.  Create an empty database environment named exactly:SQLCREATE DATABASE weather_db;
(Note: The Python script is fully modularized and will automatically initialize the structural table schema weather_reports with all bonus metrics upon its very first operational execution.)3. Environment Variable SettingsCreate a file named .env in your project's root folder to secure your access keys and database credentials:Code snippetWEATHER_API_KEY=your_actual_weatherapi_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=weather_db
4. Running the AppExecute the principal script from your terminal:Bashpython weather_app.py
💡 Usage Examples
When the system boots up, you will navigate an intuitive interactive
menu:Plaintext================ WEATHER LOG SYSTEM ================
1. Check Weather
2. View Weather History
3. View Last Weather Search
4. Hottest City Checked
5. Coldest City Checked
6. Weather Search Counter
7. Delete Weather History
8. Export Weather History
9. Statistics Dashboard
10. Exit
====================================================
Menu Action Highlights:
Option 1 (Check Weather): Type a city name (e.g., Bangalore). The system fetches the data via API, prints a structured visual summary block on-screen, and automatically logs it down inside the MySQL engine.
Option 2 (View History): Queries all database rows via fetchall() and sets up a clean, looping tabular log output tracking who, what, when, and where.
Option 9 (Statistics Dashboard): Fires high-speed SQL aggregate functions (COUNT, MAX, MIN, AVG) to print a dashboard containing aggregate temperature information.
