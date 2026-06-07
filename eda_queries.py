import sqlite3
import pandas as pd
import json
import os

def run_query(conn, query):
    return pd.read_sql_query(query, conn)

def main():
    workspace_dir = r"c:\Users\KIIT0001\Downloads\Capstone_Project"
    db_path = os.path.join(workspace_dir, "cyclistic_trips.db")
    summary_path = os.path.join(workspace_dir, "aggregated_summary.json")

    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist yet. Please run the pipeline first.")
        return

    conn = sqlite3.connect(db_path)
    print("Connected to database. Running SQL EDA queries...")

    summary_data = {}

    # Query 1: Total rides and percentages by user type
    q1 = """
    SELECT 
        member_casual, 
        COUNT(*) as total_rides,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trips), 2) as percentage
    FROM trips
    GROUP BY member_casual
    """
    df_q1 = run_query(conn, q1)
    print("\n### Query 1: Total Rides by User Type")
    print(df_q1.to_markdown(index=False))
    summary_data["user_type_totals"] = df_q1.to_dict(orient="records")

    # Query 2: Ride length statistics (in minutes) by user type
    q2 = """
    SELECT 
        member_casual,
        ROUND(MIN(ride_length) / 60.0, 2) as min_ride_length_min,
        ROUND(MAX(ride_length) / 60.0, 2) as max_ride_length_min,
        ROUND(AVG(ride_length) / 60.0, 2) as avg_ride_length_min
    FROM trips
    GROUP BY member_casual
    """
    df_q2 = run_query(conn, q2)
    print("\n### Query 2: Ride Length Stats (Minutes) by User Type")
    print(df_q2.to_markdown(index=False))
    summary_data["ride_length_stats"] = df_q2.to_dict(orient="records")

    # Query 3: Average ride length and total rides by day of the week and user type
    # 1=Sunday, 2=Monday, ..., 7=Saturday
    q3 = """
    SELECT 
        member_casual,
        day_of_week,
        COUNT(*) as total_rides,
        ROUND(AVG(ride_length) / 60.0, 2) as avg_ride_length_min
    FROM trips
    GROUP BY member_casual, day_of_week
    ORDER BY member_casual, day_of_week
    """
    df_q3 = run_query(conn, q3)
    print("\n### Query 3: Weekly Activity by User Type")
    print(df_q3.head(14).to_markdown(index=False))
    summary_data["weekly_activity"] = df_q3.to_dict(orient="records")

    # Query 4: Total rides by hour of the day and user type
    q4 = """
    SELECT 
        member_casual,
        hour_of_day,
        COUNT(*) as total_rides
    FROM trips
    GROUP BY member_casual, hour_of_day
    ORDER BY member_casual, hour_of_day
    """
    df_q4 = run_query(conn, q4)
    print("\n### Query 4: Hourly Activity by User Type (Peak Hours)")
    print(df_q4.head(10).to_markdown(index=False))
    summary_data["hourly_activity"] = df_q4.to_dict(orient="records")

    # Query 5: Rideable type popularity by user type
    q5 = """
    SELECT 
        member_casual,
        rideable_type,
        COUNT(*) as total_rides,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trips WHERE t2.member_casual = trips.member_casual), 2) as percentage
    FROM trips t2
    GROUP BY member_casual, rideable_type
    ORDER BY member_casual, total_rides DESC
    """
    df_q5 = run_query(conn, q5)
    print("\n### Query 5: Rideable Type Preferences")
    print(df_q5.to_markdown(index=False))
    summary_data["rideable_types"] = df_q5.to_dict(orient="records")

    # Query 6: Top 10 start stations for Casual riders
    q6 = """
    SELECT 
        start_station_name,
        COUNT(*) as ride_count
    FROM trips
    WHERE member_casual = 'casual' AND start_station_name IS NOT NULL AND start_station_name != ''
    GROUP BY start_station_name
    ORDER BY ride_count DESC
    LIMIT 10
    """
    df_q6 = run_query(conn, q6)
    print("\n### Query 6: Top 10 Start Stations for Casual Riders")
    print(df_q6.to_markdown(index=False))
    summary_data["top_casual_stations"] = df_q6.to_dict(orient="records")

    # Query 7: Top 10 start stations for Member riders
    q7 = """
    SELECT 
        start_station_name,
        COUNT(*) as ride_count
    FROM trips
    WHERE member_casual = 'member' AND start_station_name IS NOT NULL AND start_station_name != ''
    GROUP BY start_station_name
    ORDER BY ride_count DESC
    LIMIT 10
    """
    df_q7 = run_query(conn, q7)
    print("\n### Query 7: Top 10 Start Stations for Member Riders")
    print(df_q7.to_markdown(index=False))
    summary_data["top_member_stations"] = df_q7.to_dict(orient="records")

    # Query 8: Monthly activity by user type
    q8 = """
    SELECT 
        member_casual,
        month,
        COUNT(*) as total_rides,
        ROUND(AVG(ride_length) / 60.0, 2) as avg_ride_length_min
    FROM trips
    GROUP BY member_casual, month
    ORDER BY member_casual, month
    """
    df_q8 = run_query(conn, q8)
    print("\n### Query 8: Monthly Activity by User Type")
    print(df_q8.to_markdown(index=False))
    summary_data["monthly_activity"] = df_q8.to_dict(orient="records")

    # Query 9: Trips over 3 hours by user type (cost saving indicator)
    q9 = """
    SELECT 
        member_casual,
        COUNT(*) as total_rides_over_3h,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trips t3 WHERE t3.member_casual = trips.member_casual), 4) as percent_of_user_rides
    FROM trips
    WHERE ride_length > 10800
    GROUP BY member_casual
    """
    df_q9 = run_query(conn, q9)
    print("\n### Query 9: Trips Over 3 Hours by User Type")
    print(df_q9.to_markdown(index=False))
    summary_data["long_trips"] = df_q9.to_dict(orient="records")

    # Save summary data as JSON
    with open(summary_path, "w") as f:
        json.dump(summary_data, f, indent=4)
    print(f"\nSaved aggregated SQL summary data to {summary_path}")

    conn.close()

if __name__ == "__main__":
    main()
