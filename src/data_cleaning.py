import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim

os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"

def main():
    spark = SparkSession.builder \
        .appName("SmartBiteAnalytics-Cleaning") \
        .master("local[*]") \
        .getOrCreate()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    raw_dir = os.path.join(project_root, "data", "raw")
    output_dir = os.path.join(project_root, "data", "output")
    processed_dir = os.path.join(project_root, "data", "processed")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    print(f"--- Cleaning raw data from: {raw_dir} ---")
    
    # 1. Orders
    orders_df = spark.read.option("header", "true").option("inferSchema", "true").csv(os.path.join(raw_dir, "Orders.csv"))
    orders_clean = orders_df.dropDuplicates(["order_id"]).filter(col("order_id").isNotNull())
    orders_clean = orders_clean \
        .withColumn("cuisine_type", trim(col("cuisine_type"))) \
        .withColumn("restaurant_name", trim(col("restaurant_name"))) \
        .withColumn("day_of_the_week", trim(col("day_of_the_week"))) \
        .withColumn("total_delivery_duration", col("food_preparation_time") + col("delivery_time"))
    
    orders_pd = orders_clean.toPandas()
    orders_pd.to_csv(os.path.join(processed_dir, "cleaned_orders.csv"), index=False)
    orders_pd.to_csv(os.path.join(output_dir, "cleaned_orders.csv"), index=False)
    
    # 2. Customers
    customer_df = spark.read.option("header", "true").option("inferSchema", "true").csv(os.path.join(raw_dir, "Customer.csv"))
    customer_clean = customer_df.filter(col("Age").isNotNull()).toPandas()
    customer_clean.to_csv(os.path.join(output_dir, "cleaned_customers.csv"), index=False)
    
    # 3. Weather
    weather_df = spark.read.option("header", "true").option("inferSchema", "true").csv(os.path.join(raw_dir, "Weather.csv"))
    weather_clean = weather_df.filter(col("city").isNotNull()).toPandas()
    weather_clean.to_csv(os.path.join(output_dir, "cleaned_weather.csv"), index=False)
    
    # 4. Holidays
    holidays_df = spark.read.option("header", "true").option("inferSchema", "true").csv(os.path.join(raw_dir, "National Holidays (2021).csv"))
    holidays_clean = holidays_df.filter(col("date").isNotNull()).toPandas()
    holidays_clean.to_csv(os.path.join(output_dir, "cleaned_holidays.csv"), index=False)
    
    print("[OK] All datasets cleaned and exported successfully.")
    spark.stop()

if __name__ == "__main__":
    main()