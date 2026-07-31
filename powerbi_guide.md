# Power BI Dashboard Blueprint & Development Guide
## Cyclistic Bike-Share Case Study

Since Power BI requires a desktop GUI client to build report files (`.pbix`), this blueprint serves as a step-by-step engineering specification to construct a premium, executive-level dashboard using the cleaned dataset **`cyclistic_clean_data.csv`** which we exported to your workspace directory.

---

## 🛠️ Step 1: Connect and Prepare the Data

1. Open **Power BI Desktop**.
2. Click **Get Data** &rarr; **Text/CSV**.
3. Select **[cyclistic_clean_data.csv](file:///c:/Users/KIIT0001/Downloads/Capstone_Project/cyclistic_clean_data.csv)** from your workspace.
4. In the preview window, click **Transform Data** (Power Query).
5. Verify column data types in Power Query:
   - `ride_id`: Text
   - `rideable_type`: Text
   - `started_at`, `ended_at`: Date/Time
   - `ride_length`: Whole Number (seconds)
   - `day_of_week`, `hour_of_day`, `month`: Whole Number
   - `start_station_name`, `end_station_name`: Text
   - `member_casual`: Text

   > [!IMPORTANT]
   > **Avoid the Alphanumeric Import Gotcha:**
   > Power BI auto-detects column types by scanning the first few hundred rows of the CSV. Because the 2019 records appear first and have purely numeric `ride_id` values (e.g. `21742443`), Power BI will likely auto-detect `ride_id` as a **Whole Number** (`Int64`).
   > 
   > However, the 2020 records contain alphanumeric hexadecimal IDs (e.g. `0E1BBACD66CAF13D`). If `ride_id` remains set to **Whole Number**, all 2020 records will fail to import and result in load errors.
   > 
   > **To fix this:**
   > 1. In Power Query, click on the data type icon in the column header of `ride_id` (which shows `1 2 3` for Whole Number).
   > 2. Select **Text** from the dropdown.
   > 3. In the popup, choose **Replace current** to modify the existing column type detection step.

6. Click **Close & Apply**.

---

## 📐 Step 2: Calculated Columns & DAX Measures

To power your visualizations and cards, create these calculated columns and DAX measures:

### A. Calculated Columns (Table: `cyclistic_clean_data`)
Right-click the table name and select **New Column**:

```dax
// 1. Map Weekday Numbers to Names
Day Name = 
SWITCH(
    'cyclistic_clean_data'[day_of_week],
    1, "Sunday",
    2, "Monday",
    3, "Tuesday",
    4, "Wednesday",
    5, "Thursday",
    6, "Friday",
    7, "Saturday",
    "Unknown"
)
```

```dax
// 2. Map Month Numbers to Names
Month Name = 
SWITCH(
    'cyclistic_clean_data'[month],
    1, "January",
    2, "February",
    3, "March",
    "Unknown"
)
```

### B. DAX Measures (Table: `cyclistic_clean_data`)
Right-click the table name and select **New Measure**:

```dax
// 1. Total Rides Count
Total Rides = COUNT('cyclistic_clean_data'[ride_id])
```

```dax
// 2. Average Ride Duration in Minutes
Avg Ride Duration (Min) = AVERAGE('cyclistic_clean_data'[ride_length]) / 60
```

```dax
// 3. Percentage Share of Casual Rides
Casual Ride Share % = 
DIVIDE(
    CALCULATE([Total Rides], 'cyclistic_clean_data'[member_casual] = "casual"),
    [Total Rides],
    0
)
```

```dax
// 4. Percentage Share of Member Rides
Member Ride Share % = 
DIVIDE(
    CALCULATE([Total Rides], 'cyclistic_clean_data'[member_casual] = "member"),
    [Total Rides],
    0
)
```

```dax
// 5. Count of Extremely Long Trips (>3 hours) for Outlier analysis (Answers Q2)
Long Trips Count (>3h) = 
CALCULATE(
    [Total Rides],
    'cyclistic_clean_data'[ride_length] > 10800
)
```

---

## 🎨 Step 3: Aesthetic & Theme Configuration

To create a premium look, configure a **Dark Theme** in Power BI:
* **Background Color:** Dark Charcoal / Navy (`#0C0E17`)
* **Visual Card Background:** Dark Translucent Slate (`#1A1D2E`)
* **Text / Headers Color:** White (`#FFFFFF`)
* **Member Accents (Electric Blue):** `#00B4D8`
* **Casual Accents (Neon Teal/Green):** `#00DF9A`

---

## 📊 Step 4: Page Layouts & Visual Visualizations

Set up your dashboard with three main tabs:

### Page 1: Executive Overview
*Focuses on the high-level business goals.*

1. **KPI Card Visuals (Top Row):**
   - **Card 1:** `Total Rides` (Formatted to show **784K**)
   - **Card 2:** `Avg Ride Duration (Min)` (Formatted to show **20.0 min**)
   - **Card 3:** `Casual Ride Share %` (Formatted to show **8.63%**)
2. **Doughnut Chart (Top Left):**
   - **Legend:** `member_casual`
   - **Values:** `Total Rides`
   - **Colors:** Member = Electric Blue (`#00B4D8`), Casual = Neon Teal (`#00DF9A`)
   - *Answers: The baseline user-type trip split.*
3. **Stacked Bar Chart (Bottom Row):**
   - **X-Axis:** `Month Name` (Ordered Jan, Feb, Mar)
   - **Y-Axis:** `Total Rides`
   - **Legend:** `member_casual`
   - *Answers Q2/Q3: Shows the dramatic 170% surge of casuals in March (seasonality).*

---

### Page 2: Behavioral Analysis (Members vs. Casuals)
*Focuses on answering Q1: How do they use bikes differently?*

1. **Grouped Bar Chart (Weekly Vol):**
   - **X-Axis:** `Day Name` (Sorted Sunday to Saturday)
   - **Y-Axis:** `Total Rides`
   - **Legend:** `member_casual`
   - *Answers: Demonstrates that casuals peak on weekends, members flatline weekdays.*
2. **Line Chart (Hourly distribution):**
   - **X-Axis:** `hour_of_day` (0 to 23)
   - **Y-Axis:** `Total Rides`
   - **Legend:** `member_casual`
   - *Answers: Reveals the double-commute spikes at 8 AM and 5 PM for members, and the smooth afternoon curve for casuals.*
3. **Clustered Column Chart (Average Duration):**
   - **X-Axis:** `member_casual`
   - **Y-Axis:** `Avg Ride Duration (Min)`
   - *Answers Q2: Visually contrasts casuals' ~90-min trips against members' ~13-min trips, proving casuals are taking long leisure rides.*

---

### Page 3: Location Hotspots (Geographic Targets)
*Focuses on answering Q3: Where to deploy digital media campaigns?*

1. **Horizontal Bar Chart (Top Start Stations):**
   - **Y-Axis:** `start_station_name`
   - **X-Axis:** `Total Rides`
   - **Visual Filters:** Add `member_casual` to the visual-level filter and set it to **`casual`**.
   - *Answers Q3: Shows top hotspots like Streeter Dr & Grand Ave for target marketing.*
2. **Slicers (Page Filters):**
   - Add a Slicer for `Month Name` (dropdown).
   - Add a Slicer for `Day Name` (multiselect list).
   - *Action: Allows the marketing team to slice the stations by weekend vs. weekday or month to locate active casual clusters.*

---

## 🎯 How this answers the Business Task in Power BI

By opening this dashboard, Lily Moreno can immediately select **"casual"** in a slicer and observe:
1. **The Cost-Saving Selling Point (Q2):** The card showing average trip length at **89.8 minutes** directly supports marketing copy illustrating how casuals are overpaying under standard single-pass structures.
2. **The Geo-Targeting Strategy (Q3):** Slicing top starting stations by weekends shows them exactly where to place signage and geofenced digital ads.
3. **The Seasonal Campaign Window (Q2/Q3):** Slicing by month shows that digital campaigns must be funded and active by early March to catch the massive ridership upswing.
