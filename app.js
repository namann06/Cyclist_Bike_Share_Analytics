document.addEventListener("DOMContentLoaded", () => {
    // Tab Switching Logic
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            // Deactivate all buttons and tabs
            tabBtns.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            // Activate current button and tab
            btn.classList.add("active");
            document.getElementById(`tab-${targetTab}`).classList.add("active");
        });
    });

    // Fetch Aggregated Data and Render Interactive Charts
    fetch("aggregated_summary.json")
        .then(response => response.json())
        .then(data => {
            console.log("Loaded data:", data);
            
            // Update Stat Cards with dynamic values (Optional / Safeguard)
            if (data.user_type_totals && data.ride_length_stats) {
                const casualTotal = data.user_type_totals.find(x => x.member_casual === 'casual');
                const memberTotal = data.user_type_totals.find(x => x.member_casual === 'member');
                const casualStats = data.ride_length_stats.find(x => x.member_casual === 'casual');
                const memberStats = data.ride_length_stats.find(x => x.member_casual === 'member');
                
                const totalRidesVal = (casualTotal?.total_rides || 0) + (memberTotal?.total_rides || 0);
                
                document.getElementById("stat-total").innerText = totalRidesVal.toLocaleString();
                
                if (casualTotal) {
                    document.getElementById("stat-casual").innerText = `${casualTotal.total_rides.toLocaleString()} (${casualTotal.percentage}%)`;
                }
                if (casualStats) {
                    document.getElementById("stat-casual-duration").innerText = `${casualStats.avg_ride_length_min.toFixed(1)} min`;
                }
                if (memberStats) {
                    document.getElementById("stat-member-duration").innerText = `${memberStats.avg_ride_length_min.toFixed(1)} min`;
                }
            }

            // Render Chart 1: User Type Shares (Doughnut)
            renderUserTypeChart(data.user_type_totals);

            // Render Chart 2: Average Ride Lengths (Bar)
            renderDurationChart(data.ride_length_stats);

            // Render Chart 3: Weekly Activity (Grouped Bar)
            renderWeeklyChart(data.weekly_activity);

            // Render Chart 4: Hourly Activity (Line)
            renderHourlyChart(data.hourly_activity);

            // Render Chart 5 & 6: Stations (Horizontal Bar)
            renderStationChart("chart-stations-casual", data.top_casual_stations, "#00df9a", "Casual Trips");
            renderStationChart("chart-stations-member", data.top_member_stations, "#00b4d8", "Member Trips");

            // Render Chart 7: Monthly Seasonality (Grouped Bar)
            renderMonthlyTrendsChart(data.monthly_activity);
        })
        .catch(err => {
            console.error("Error loading aggregated data. Using fallback data. Details:", err);
            // Fallback rendering in case server is not run (static view)
            renderFallbackCharts();
        });
});

// Chart 1: User Type Doughnut Chart
function renderUserTypeChart(totals) {
    const ctx = document.getElementById("chart-user-type").getContext("2d");
    
    // Default fallback values
    let casualVal = 67692;
    let memberVal = 716593;
    
    if (totals) {
        casualVal = totals.find(x => x.member_casual === 'casual')?.total_rides || casualVal;
        memberVal = totals.find(x => x.member_casual === 'member')?.total_rides || memberVal;
    }

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Casual', 'Member'],
            datasets: [{
                data: [casualVal, memberVal],
                backgroundColor: ['#00df9a', '#00b4d8'],
                borderColor: '#1a1d2e',
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#e2e8f0', font: { family: 'Outfit', size: 12 } }
                }
            }
        }
    });
}

// Chart 2: Average Duration Bar Chart
function renderDurationChart(stats) {
    const ctx = document.getElementById("chart-avg-duration").getContext("2d");
    
    let casualDuration = 89.79;
    let memberDuration = 13.32;
    
    if (stats) {
        casualDuration = stats.find(x => x.member_casual === 'casual')?.avg_ride_length_min || casualDuration;
        memberDuration = stats.find(x => x.member_casual === 'member')?.avg_ride_length_min || memberDuration;
    }

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Casual', 'Member'],
            datasets: [{
                label: 'Avg Duration (Minutes)',
                data: [casualDuration, memberDuration],
                backgroundColor: ['#00df9a', '#00b4d8'],
                borderRadius: 10,
                barThickness: 45
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#e2e8f0', font: { family: 'Outfit', size: 12, weight: 'bold' } }
                }
            }
        }
    });
}

// Chart 3: Weekly Activity (Grouped Bar Chart)
function renderWeeklyChart(weeklyData) {
    const ctx = document.getElementById("chart-weekly").getContext("2d");
    const weekLabels = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    
    // Arrays indexed from day_of_week 1 to 7 (index 0 to 6)
    let casualTrips = [0, 0, 0, 0, 0, 0, 0];
    let memberTrips = [0, 0, 0, 0, 0, 0, 0];

    if (weeklyData) {
        weeklyData.forEach(row => {
            const idx = row.day_of_week - 1;
            if (row.member_casual === 'casual') {
                casualTrips[idx] = row.total_rides;
            } else {
                memberTrips[idx] = row.total_rides;
            }
        });
    } else {
        // Fallback Q1 aggregate counts
        casualTrips = [18586, 5580, 7289, 7658, 7127, 7996, 13456];
        memberTrips = [59716, 109873, 127391, 121326, 124598, 114624, 59065];
    }

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weekLabels,
            datasets: [
                {
                    label: 'Casual Riders',
                    data: casualTrips,
                    backgroundColor: '#00df9a',
                    borderRadius: 6
                },
                {
                    label: 'Annual Members',
                    data: memberTrips,
                    backgroundColor: '#00b4d8',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e2e8f0', font: { family: 'Outfit' } }
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                }
            }
        }
    });
}

// Chart 4: Hourly Activity (Line Chart)
function renderHourlyChart(hourlyData) {
    const ctx = document.getElementById("chart-hourly").getContext("2d");
    const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
    
    let casualHourly = Array(24).fill(0);
    let memberHourly = Array(24).fill(0);

    if (hourlyData) {
        hourlyData.forEach(row => {
            const hr = row.hour_of_day;
            if (row.member_casual === 'casual') {
                casualHourly[hr] = row.total_rides;
            } else {
                memberHourly[hr] = row.total_rides;
            }
        });
    } else {
        // Fallback trends representation
        casualHourly = [465, 331, 248, 145, 95, 196, 471, 1010, 1832, 1869, 2100, 2900, 3500, 3800, 4100, 4200, 4100, 3900, 3400, 2700, 1900, 1400, 950, 650];
        memberHourly = [4500, 2500, 1400, 800, 1200, 7500, 26000, 58000, 64000, 42000, 31000, 35000, 41000, 39000, 36000, 45000, 68000, 72000, 48000, 32000, 21000, 14000, 9500, 6500];
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'Casual Riders',
                    data: casualHourly,
                    borderColor: '#00df9a',
                    backgroundColor: 'rgba(0, 223, 154, 0.1)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 3,
                    pointRadius: 3
                },
                {
                    label: 'Annual Members',
                    data: memberHourly,
                    borderColor: '#00b4d8',
                    backgroundColor: 'rgba(0, 180, 216, 0.1)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 3,
                    pointRadius: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e2e8f0', font: { family: 'Outfit' } }
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                }
            }
        }
    });
}

// Chart 5 & 6: Stations Horizontal Bar Chart
function renderStationChart(canvasId, stationData, barColor, labelTag) {
    const ctx = document.getElementById(canvasId).getContext("2d");
    
    let labels = [];
    let counts = [];
    
    if (stationData && stationData.length > 0) {
        labels = stationData.map(x => x.start_station_name.length > 25 ? x.start_station_name.substring(0, 22) + "..." : x.start_station_name);
        counts = stationData.map(x => x.ride_count);
    } else {
        // Fallback placeholders depending on type
        if (canvasId.includes("casual")) {
            labels = ["Streeter Dr & Grand", "Lake Shore & Monroe", "Shedd Aquarium", "Millennium Park", "Michigan & Oak", "Michigan & Wash", "Dusable Harbor", "Adler Planetarium", "Theater on Lake", "Lake Shore & North"];
            counts = [2741, 2731, 1829, 1404, 1015, 838, 832, 825, 793, 603];
        } else {
            labels = ["Canal & Adams", "Clinton & Wash", "Clinton & Madison", "Kingsbury & Kinzie", "Columbus & Randolph", "Canal & Madison", "Franklin & Monroe", "Michigan & Wash", "Larrabee & Kingsbury", "Clinton & Lake"];
            counts = [13754, 13392, 12838, 8687, 8467, 7861, 6973, 6673, 6443, 6420];
        }
    }

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: labelTag,
                data: counts,
                backgroundColor: barColor,
                borderRadius: 5
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#cbd5e1', font: { family: 'Outfit', size: 10 } }
                }
            }
        }
    });
}

function renderFallbackCharts() {
    renderUserTypeChart(null);
    renderDurationChart(null);
    renderWeeklyChart(null);
    renderHourlyChart(null);
    renderStationChart("chart-stations-casual", null, "#00df9a", "Casual Trips");
    renderStationChart("chart-stations-member", null, "#00b4d8", "Member Trips");
    renderMonthlyTrendsChart(null);
}

// Chart 7: Monthly Seasonality Bar Chart
function renderMonthlyTrendsChart(monthlyData) {
    const ctx = document.getElementById("chart-monthly-trends").getContext("2d");
    const monthLabels = ["January", "February", "March"];
    
    let casualMonthly = [0, 0, 0];
    let memberMonthly = [0, 0, 0];

    if (monthlyData) {
        monthlyData.forEach(row => {
            const idx = row.month - 1; // Jan=1, Feb=2, March=3
            if (row.member_casual === 'casual') {
                casualMonthly[idx] = row.total_rides;
            } else {
                memberMonthly[idx] = row.total_rides;
            }
        });
    } else {
        // Fallback Q1 monthly aggregate counts
        casualMonthly = [12344, 14907, 40441];
        memberMonthly = [233562, 218960, 264071];
    }

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthLabels,
            datasets: [
                {
                    label: 'Casual Riders',
                    data: casualMonthly,
                    backgroundColor: '#00df9a',
                    borderRadius: 6
                },
                {
                    label: 'Annual Members',
                    data: memberMonthly,
                    backgroundColor: '#00b4d8',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e2e8f0', font: { family: 'Outfit' } }
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                }
            }
        }
    });
}
