import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    workspace_dir = r"c:\Users\KIIT0001\Downloads\Capstone_Project"
    db_path = os.path.join(workspace_dir, "cyclistic_trips.db")
    plots_dir = os.path.join(workspace_dir, "plots")

    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist yet. Please run the pipeline first.")
        return

    os.makedirs(plots_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    print("Connected to database. Generating Matplotlib & Seaborn plots...")

    # Set theme style and palette
    sns.set_theme(style="whitegrid")
    custom_palette = {"member": "#00b4d8", "casual": "#00df9a"}
    week_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    # Plot 1: Total Ride Share by User Type
    print("Generating Plot 1: Total Rides...")
    q1 = "SELECT member_casual, COUNT(*) as ride_count FROM trips GROUP BY member_casual"
    df_q1 = pd.read_sql_query(q1, conn)
    
    plt.figure(figsize=(7, 6))
    plt.pie(df_q1['ride_count'], labels=df_q1['member_casual'].str.capitalize(), autopct='%1.1f%%',
            startangle=140, colors=[custom_palette[x] for x in df_q1['member_casual']], 
            textprops={'fontsize': 12, 'weight': 'bold'})
    plt.title("Total Ride Volume Share (Q1 2019 & Q1 2020)", fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "ride_count_shares.png"), dpi=150)
    plt.close()

    # Plot 2: Average Ride Duration Comparison
    print("Generating Plot 2: Average Ride Duration...")
    q2 = "SELECT member_casual, AVG(ride_length) / 60.0 as avg_duration_min FROM trips GROUP BY member_casual"
    df_q2 = pd.read_sql_query(q2, conn)
    
    plt.figure(figsize=(6, 5))
    ax = sns.barplot(data=df_q2, x="member_casual", y="avg_duration_min", palette=custom_palette)
    plt.title("Average Ride Length by User Type", fontsize=14, weight='bold', pad=15)
    plt.xlabel("User Type", fontsize=12)
    plt.ylabel("Average Duration (Minutes)", fontsize=12)
    ax.set_xticklabels([x.get_text().capitalize() for x in ax.get_xticklabels()])
    
    # Add values on top of bars
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.2f} min", (p.get_x() + p.get_width() / 2., p.get_height() + 0.5),
                    ha='center', va='center', fontsize=11, color='black', weight='bold',
                    xytext=(0, 5), textcoords='offset points')
    
    plt.ylim(0, df_q2['avg_duration_min'].max() + 5)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "avg_ride_duration.png"), dpi=150)
    plt.close()

    # Plot 3: Weekly Activity trends (total rides)
    print("Generating Plot 3: Weekly Ride Trends...")
    q3 = "SELECT member_casual, day_of_week, COUNT(*) as total_rides FROM trips GROUP BY member_casual, day_of_week"
    df_q3 = pd.read_sql_query(q3, conn)
    df_q3['day_name'] = df_q3['day_of_week'].apply(lambda x: week_names[x - 1])
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_q3, x="day_name", y="total_rides", hue="member_casual", palette=custom_palette, order=week_names)
    plt.title("Rides Volume by Day of the Week", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Day of the Week", fontsize=12)
    plt.ylabel("Total Rides", fontsize=12)
    plt.legend(title="User Type")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "weekly_ride_trends.png"), dpi=150)
    plt.close()

    # Plot 4: Hourly Activity trends (Rides per hour)
    print("Generating Plot 4: Hourly Ride Trends...")
    q4 = "SELECT member_casual, hour_of_day, COUNT(*) as total_rides FROM trips GROUP BY member_casual, hour_of_day"
    df_q4 = pd.read_sql_query(q4, conn)
    
    plt.figure(figsize=(11, 6))
    sns.lineplot(data=df_q4, x="hour_of_day", y="total_rides", hue="member_casual", palette=custom_palette, marker="o", linewidth=2.5)
    plt.title("Hourly Ride Distribution (Time of Day)", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Hour of Day (24h Format)", fontsize=12)
    plt.ylabel("Number of Rides", fontsize=12)
    plt.xticks(range(0, 24))
    plt.legend(title="User Type")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "hourly_ride_trends.png"), dpi=150)
    plt.close()

    # Plot 5: Top 10 start stations for casual riders
    print("Generating Plot 5: Top Casual Stations...")
    q5 = """
    SELECT start_station_name, COUNT(*) as ride_count 
    FROM trips 
    WHERE member_casual = 'casual' AND start_station_name IS NOT NULL AND start_station_name != ''
    GROUP BY start_station_name 
    ORDER BY ride_count DESC 
    LIMIT 10
    """
    df_q5 = pd.read_sql_query(q5, conn)
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_q5, y="start_station_name", x="ride_count", color="#00df9a")
    plt.title("Top 10 Start Stations for Casual Riders", fontsize=14, weight='bold', pad=15)
    plt.ylabel("Station Name", fontsize=12)
    plt.xlabel("Number of Trips", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "top_casual_stations.png"), dpi=150)
    plt.close()

    # Plot 6: Monthly trends
    print("Generating Plot 6: Monthly Ride Trends...")
    q6 = "SELECT member_casual, month, COUNT(*) as total_rides FROM trips GROUP BY member_casual, month"
    df_q6 = pd.read_sql_query(q6, conn)
    month_names = {1: "January", 2: "February", 3: "March"}
    df_q6['month_name'] = df_q6['month'].map(month_names)
    
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(data=df_q6, x="month_name", y="total_rides", hue="member_casual", palette=custom_palette, order=["January", "February", "March"])
    plt.title("Rides Volume by Month (Q1 Seasonality)", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Total Rides", fontsize=12)
    plt.legend(title="User Type")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "monthly_ride_trends.png"), dpi=150)
    plt.close()

    print("All plots generated successfully and saved in plots/ folder!")
    conn.close()

if __name__ == "__main__":
    main()
