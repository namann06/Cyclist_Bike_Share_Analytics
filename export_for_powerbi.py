import sqlite3
import pandas as pd
import os

def main():
    workspace_dir = r"c:\Users\KIIT0001\Downloads\Capstone_Project"
    db_path = os.path.join(workspace_dir, "cyclistic_trips.db")
    csv_out_path = os.path.join(workspace_dir, "cyclistic_clean_data.csv")

    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist yet. Please run the pipeline first.")
        return

    print("Connecting to SQLite database...")
    conn = sqlite3.connect(db_path)
    
    print("Fetching cleaned trip data...")
    # Select key columns for Power BI to keep file size optimized
    query = """
    SELECT 
        ride_id,
        rideable_type,
        started_at,
        ended_at,
        ride_length,
        day_of_week,
        hour_of_day,
        month,
        start_station_name,
        end_station_name,
        member_casual
    FROM trips
    """
    df = pd.read_sql_query(query, conn)
    print(f"Loaded {len(df)} records. Exporting to CSV...")
    
    df.to_csv(csv_out_path, index=False)
    print(f"Success! Exported clean dataset to {csv_out_path}")
    
    conn.close()

if __name__ == "__main__":
    main()
