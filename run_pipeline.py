import subprocess
import sys
import os

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), "src", script_name)
    print(f"--> Running: {script_name}")
    
    # Force UTF-8 encoding for subprocess to prevent Windows charmap errors
    result = subprocess.run(
        [sys.executable, script_path], 
        capture_output=True, 
        text=True, 
        encoding="utf-8", 
        errors="replace"
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
        
    if result.returncode != 0:
        print(f"[X] Error: {script_name} failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    else:
        print(f"[OK] Success: {script_name} completed successfully.\n")

def main():
    steps = [
        "data_ingestion.py",
        "data_cleaning.py",
        "demand_analysis.py",
        "delivery_analysis.py",
        "spark_sql_analysis.py",
        "export_results.py"
    ]
    
    print("==================================================")
    print("STARTING SPARK MULTI-SOURCE PIPELINE")
    print("==================================================")
    
    for step in steps:
        run_script(step)
        
    print("==================================================")
    print("ALL PIPELINE STEPS COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    main()