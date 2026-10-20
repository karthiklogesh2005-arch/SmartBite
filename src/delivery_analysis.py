import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, min, max

os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"

def main():
    spark = SparkSession.builder \
        .appName("SmartBiteAnalytics-DeliveryAnalysis") \
        .master("local[*]") \
        .getOrCreate()
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    csv_file = os.path.join(project_root, "data", "processed", "cleaned_orders.csv")
    output_dir = os.path.join(project_root, "data", "output")
    
    orders_df = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_file)
    
    delivery_perf = orders_df.groupBy("cuisine_type") \
        .agg(
            avg("food_preparation_time").alias("avg_prep_time"),
            avg("delivery_time").alias("avg_delivery_time"),
            avg("total_delivery_duration").alias("avg_total_duration"),
            min("total_delivery_duration").alias("min_total_duration"),
            max("total_delivery_duration").alias("max_total_duration")
        ) \
        .orderBy(col("avg_total_duration").desc()) \
        .toPandas()
        
    delivery_perf.to_csv(os.path.join(output_dir, "delivery_performance.csv"), index=False)
    
    print("[OK] Delivery performance analysis completed.")
    spark.stop()

if __name__ == "__main__":
    main()