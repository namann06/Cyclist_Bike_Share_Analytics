import os
import urllib.request
import zipfile
import pandas as pd
import sqlite3
import time

def main():
    workspace_dir = r"c:\Users\KIIT0001\Downloads\Capstone_Project"
    data_dir = os.path.join(workspace_dir, "data")
    db_path = os.path.join(workspace_dir, "cyclistic_trips.db")

    # Ensure directories exist
    os.makedirs(data_dir, exist_ok=True)

    urls = {
        "Divvy_Trips_2019_Q1.zip": "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
        "Divvy_Trips_2020_Q1.zip": "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip"
    }

    # Step 1: Download zip files
    for filename, url in urls.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(f"Downloading {filename} from {url}...")
            start_time = time.time()
            urllib.request.urlretrieve(url, filepath)
            print(f"Downloaded {filename} in {time.time() - start_time:.2f} seconds.")
        else:
            print(f"{filename} already exists. Skipping download.")

    # Step 2: Unzip files
    csv_files = {}
    for filename in urls.keys():
        filepath = os.path.join(data_dir, filename)
        print(f"Unzipping {filename}...")
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
            # Find the extracted CSV file
            for file in zip_ref.namelist():
                if file.endswith('.csv') and not file.startswith('__MACOSX'):
                    key = "2019" if "2019" in filename else "2020"
                    csv_files[key] = os.path.join(data_dir, file)
                    print(f"Extracted CSV: {file}")

    print("CSV Extraction complete.", csv_files)

    # Step 3: Connect to SQLite Database
    print(f"Connecting to SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Drop existing trips table 
    cursor.execute("DROP TABLE IF EXISTS trips")
    conn.commit()

    # Step 4: Process 2019 Q1
    if "2019" in csv_files:
        csv_path = csv_files["2019"]
        print(f"Processing 2019 Q1 data from {csv_path}...")
        
        # Load 2019 Q1
        df_19 = pd.read_csv(csv_path)
        print(f"Original 2019 shape: {df_19.shape}")
        
        # Column renames to align with 2020
        rename_dict = {
            'trip_id': 'ride_id',
            'bikeid': 'rideable_type',  
            'start_time': 'started_at',
            'end_time': 'ended_at',
            'from_station_name': 'start_station_name',
            'from_station_id': 'start_station_id',
            'to_station_name': 'end_station_name',
            'to_station_id': 'end_station_id',
            'usertype': 'member_casual'
        }
        df_19.rename(columns=rename_dict, inplace=True)
        
        # Select and align columns
        columns_to_keep = [
            'ride_id', 'rideable_type', 'started_at', 'ended_at',
            'start_station_name', 'start_station_id', 'end_station_name', 'end_station_id',
            'member_casual'
        ]
        df_19 = df_19[columns_to_keep]

        # Convert types
        df_19['ride_id'] = df_19['ride_id'].astype(str)
        df_19['start_station_id'] = df_19['start_station_id'].astype(str)
        df_19['end_station_id'] = df_19['end_station_id'].astype(str)
        
        # Map values
        # member_casual: Subscriber -> member, Customer -> casual
        df_19['member_casual'] = df_19['member_casual'].map({
            'Subscriber': 'member',
            'Customer': 'casual'
        })
        
       
        df_19['rideable_type'] = 'docked_bike'

        # Convert times
        df_19['started_at'] = pd.to_datetime(df_19['started_at'])
        df_19['ended_at'] = pd.to_datetime(df_19['ended_at'])

        # Calculate durations and filter
        df_19['ride_length'] = (df_19['ended_at'] - df_19['started_at']).dt.total_seconds()
        
        # Remove trips < 60 seconds (1 minute) or where started_at is after ended_at
        df_19 = df_19[df_19['ride_length'] >= 60]
        
        # Extract fields
        # day_of_week: 1=Sunday, 7=Saturday
        df_19['day_of_week'] = ((df_19['started_at'].dt.dayofweek + 1) % 7) + 1
        df_19['hour_of_day'] = df_19['started_at'].dt.hour
        df_19['month'] = df_19['started_at'].dt.month

        # Save to SQLite
        print(f"Saving 2019 Q1 cleaned data to database. Row count: {len(df_19)}")
        df_19.to_sql('trips', conn, if_exists='append', index=False)
        print("2019 Q1 Ingestion Completed.")

    # Step 5: Process 2020 Q1
    if "2020" in csv_files:
        csv_path = csv_files["2020"]
        print(f"Processing 2020 Q1 data from {csv_path}...")
        
        # Load 2020 Q1
        df_20 = pd.read_csv(csv_path)
        print(f"Original 2020 shape: {df_20.shape}")

        # Ensure correct column names (already matching 2020 standards)
        columns_to_keep = [
            'ride_id', 'rideable_type', 'started_at', 'ended_at',
            'start_station_name', 'start_station_id', 'end_station_name', 'end_station_id',
            'member_casual'
        ]
        df_20 = df_20[columns_to_keep]

        # Convert types
        df_20['ride_id'] = df_20['ride_id'].astype(str)
        df_20['start_station_id'] = df_20['start_station_id'].astype(str)
        df_20['end_station_id'] = df_20['end_station_id'].astype(str)
        
        # Convert times
        df_20['started_at'] = pd.to_datetime(df_20['started_at'])
        df_20['ended_at'] = pd.to_datetime(df_20['ended_at'])

        # Calculate durations and filter
        df_20['ride_length'] = (df_20['ended_at'] - df_20['started_at']).dt.total_seconds()
        
        # Remove trips < 60 seconds (1 minute) or where started_at is after ended_at
        df_20 = df_20[df_20['ride_length'] >= 60]
        
        # Extract fields
        # day_of_week: 1=Sunday, 7=Saturday
        df_20['day_of_week'] = ((df_20['started_at'].dt.dayofweek + 1) % 7) + 1
        df_20['hour_of_day'] = df_20['started_at'].dt.hour
        df_20['month'] = df_20['started_at'].dt.month

        # Save to SQLite
        print(f"Saving 2020 Q1 cleaned data to database. Row count: {len(df_20)}")
        df_20.to_sql('trips', conn, if_exists='append', index=False)
        print("2020 Q1 Ingestion Completed.")

    # Create Indexes for optimization
    print("Creating database indexes for optimization...")
    cursor.execute("CREATE INDEX idx_user_type ON trips(member_casual)")
    cursor.execute("CREATE INDEX idx_weekday ON trips(day_of_week)")
    cursor.execute("CREATE INDEX idx_hour ON trips(hour_of_day)")
    cursor.execute("CREATE INDEX idx_start_station ON trips(start_station_name)")
    conn.commit()
    
    # Get total row count
    cursor.execute("SELECT COUNT(*) FROM trips")
    total_rows = cursor.fetchone()[0]
    print(f"Data Pipeline completed successfully! Total records loaded in SQLite table 'trips': {total_rows}")
    
    conn.close()

if __name__ == "__main__":
    main()
