import pandas as pd
import requests
import time
import os

def fetch_historical_data():
    # Load coordinates
    if not os.path.exists("data/municipality_coords.csv"):
        print("Error: data/municipality_coords.csv not found!")
        return
    
    coords_df = pd.read_csv("data/municipality_coords.csv")
    history_results = []
    
    # Define the year to analyze
    YEAR = 2024
    START = f"{YEAR}-01-01"
    END = f"{YEAR}-12-31"

    print(f"Starting historical data collection for {YEAR}...")

    for _, row in coords_df.iterrows():
        code = str(row['code']).zfill(3)
        name = row['name']
        lat, lon = row['lat'], row['lng']

        try:
            # --- 1. Fetch Weather Stats (Rain, Sun, Fog) ---
            w_url = "https://archive-api.open-meteo.com/v1/archive"
            w_params = {
                "latitude": lat, "longitude": lon,
                "start_date": START, "end_date": END,
                "daily": "weather_code,temperature_2m_mean",
                "timezone": "Europe/Berlin"
            }
            w_res = requests.get(w_url, params=w_params).json()
            daily = w_res.get("daily", {})
            codes = daily.get("weather_code", [])
            temps = daily.get("temperature_2m_mean", [])

            # --- 2. Fetch Air Quality (European AQI) ---
            # We use the hourly average for the year
            a_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
            a_params = {
                "latitude": lat, "longitude": lon,
                "start_date": START, "end_date": END,
                "hourly": "european_aqi",
                "timezone": "Europe/Berlin"
            }
            a_res = requests.get(a_url, params=a_params).json()
            aqi_list = a_res.get("hourly", {}).get("european_aqi", [])

            # --- 3. Calculate Stats ---
            # WMO Codes: 0-1 (Sun), 45-48 (Fog), 51-67 (Rain)
            sunny_days = sum(1 for c in codes if c <= 1)
            rainy_days = sum(1 for c in codes if 51 <= c <= 67)
            foggy_days = sum(1 for c in codes if c in [45, 48])
            avg_temp = sum(temps) / len(temps) if temps else 0
            
            # AQI: Lower is better (0-20 is Excellent, 20-40 Good, etc.)
            valid_aqi = [a for a in aqi_list if a is not None]
            avg_aqi = sum(valid_aqi) / len(valid_aqi) if valid_aqi else 0

            history_results.append({
                "code": code,
                "name": name,
                "avg_temp_yearly": round(avg_temp, 2),
                "sunny_days_count": sunny_days,
                "rainy_days_count": rainy_days,
                "foggy_days_count": foggy_days,
                "avg_aqi": round(avg_aqi, 2)
            })

            print(f"Processed {name} (AQI: {round(avg_aqi, 2)})")
            time.sleep(0.05) # Tiny sleep to prevent rate limiting

        except Exception as e:
            print(f"Error processing {name}: {e}")

    # Save to CSV
    res_df = pd.DataFrame(history_results)
    res_df.to_csv("data/municipality_history.csv", index=False)
    print("DONE! Saved to data/municipality_history.csv")

if __name__ == "__main__":
    fetch_historical_data()