import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    output_dir = os.path.join(project_root, "data", "output")
    
    expected_files = [
        "cleaned_orders.csv",
        "cleaned_customers.csv",
        "cleaned_weather.csv",
        "cleaned_holidays.csv",
        "demand_by_day.csv",
        "demand_by_cuisine.csv",
        "delivery_performance.csv",
        "top_restaurants_sql.csv"
    ]
    
    print(f"--- Verifying analytical outputs in: {output_dir} ---")
    missing = []
    
    for filename in expected_files:
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            print(f"[OK] Found: {filename}")
        else:
            print(f"[ERROR] Missing: {filename}")
            missing.append(filename)
            
    if missing:
        print(f"[WARNING] {len(missing)} expected output files are missing.")
    else:
        print("[SUCCESS] All analytical outputs successfully verified and consolidated!")

if __name__ == "__main__":
    main()