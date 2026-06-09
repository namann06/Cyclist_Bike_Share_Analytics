# Cyclistic Bike-Share Capstone Project - Q1 2019 & Q1 2020 Analysis

Welcome to the Cyclistic Bike-Share capstone project! This repository contains a complete, reproducible data pipeline, SQL-based exploratory data analysis (EDA), python-generated visualizations, and an interactive Power BI dashboard.

## Project Deliverables

This project answers the business question assigned by Lily Moreno, Director of Marketing:
**"How do annual members and casual riders use Cyclistic bikes differently?"**

### Contents
1. **`data_pipeline.py`**: A python script that downloads the raw datasets (`Divvy_Trips_2019_Q1.zip` and `Divvy_Trips_2020_Q1.zip`), extracts them, cleans them, standardizes column formats, and writes them into an SQLite database table (`trips`).
2. **`eda_queries.py`**: A script that executes multiple analytical SQL queries against the SQLite database to summarize metrics by member type, day of week, hour of day, and start station. It exports results to `aggregated_summary.json`.
3. **`generate_plots.py`**: A script that queries the database and outputs 5 high-resolution Seaborn visualizations in the `plots/` folder.
4. **`PowerBI/Cyclistic_Bike_Share_Analytics.pbix`**: An interactive, premium Power BI dashboard presenting the full business analysis, including key performance indicators (KPIs), weekday/hourly behavioral curves, and geographical marketing hotspots. 

---

## How to Run the Project

### Prerequisites
Make sure you have Python (Anaconda environment recommended) and **Power BI Desktop** installed.

### Step 1: Run the Data Pipeline
Execute the Python script to ingest, clean, and populate the SQLite database.
```bash
python data_pipeline.py
```
*Expected Ingestion Count: 784,285 cleaned trips loaded into SQLite database `cyclistic_trips.db`.*

### Step 2: Run SQL EDA Queries
Run the analytical SQL queries to inspect the data and generate the JSON summary file.
```bash
python eda_queries.py
```
*This will print Markdown tables of the SQL query results directly to the console and create `aggregated_summary.json`.*

### Step 3: Generate Matplotlib & Seaborn Plots
Generate the high-resolution static plots.
```bash
python generate_plots.py
```
*This will write five visualization PNG files into the `plots/` directory.*

### Step 4: View the Power BI Dashboard
Open the interactive Power BI dashboard to explore the executive insights and visual analysis:
1. Open the file **`PowerBI/Cyclistic_Bike_Share_Analytics.pbix`** using **Power BI Desktop**.
2. If you need to rebuild or customize the dashboard steps, refer to the detailed build guide in [powerbi_guide.md](file:///c:/Users/KIIT0001/Downloads/Capstone_Project/powerbi_guide.md).

---

## Data Summary & Key Insights

1. **Trip Share:** Annual members account for the vast majority of rides (**91.37%**), while casual riders account for **8.63%** of Q1 rides.
2. **Trip Length:** Casual riders take significantly longer rides on average (**89.79 minutes**) compared to members (**13.32 minutes**).
3. **Weekly Volume:** Members exhibit heavy usage on weekdays (Monday through Friday), peaking during routine commuting days. Casual riders show their highest volumes on weekends (Saturday and Sunday).
4. **Hourly Spikes:** Members show sharp peak spikes at **8:00 AM** and **5:00 PM** (standard office commute hours). Casual riders show a single, gradual peak between **12:00 PM** and **3:00 PM** (leisure curve).
5. **Recreational Hotspots:** The top casual start stations are highly clustered around tourist and park locations (e.g., *Streeter Dr & Grand Ave*, *Lake Shore Dr & Monroe St*, *Shedd Aquarium*, *Millennium Park*). Member start stations cluster around business hubs and major train transit centers (e.g., *Canal St & Adams St*, *Clinton St & Washington Blvd*).
