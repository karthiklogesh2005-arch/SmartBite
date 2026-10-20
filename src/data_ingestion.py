import os
from pyspark.sql import SparkSession

os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"

def main():
    spark = SparkSession.builder \
        .appName("SmartBiteAnalytics-Ingestion") \
        .master("local[*]") \
        .getOrCreate()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    raw_dir = os.path.join(project_root, "data", "raw")
    
    print(f"--- Loading raw files from: {raw_dir} ---")
    
    orders_df = spark.read.option("header", "true").option("inferSchema", "true").csv(os.path.join(raw_dir, "Orders.csv"))
    customer_df = spark.read.option("header", "true").option("inferSchema", "true").csv(os.path.join(raw_dir, "Customer.csv"))
    weather_df = spark.read.option("header", "true").option("inferSchema", "true").csv(os.path.join(raw_dir, "Weather.csv"))
    holidays_df = spark.read.option("header", "true").option("inferSchema", "true").csv(os.path.join(raw_dir, "National Holidays (2021).csv"))
    
    print(f"[OK] Orders count: {orders_df.count()}")
    print(f"[OK] Customer count: {customer_df.count()}")
    print(f"[OK] Weather count: {weather_df.count()}")
    print(f"[OK] Holidays count: {holidays_df.count()}")
    
    spark.stop()

if __name__ == "__main__":
    main()