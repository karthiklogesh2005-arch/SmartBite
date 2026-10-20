import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, sum

os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"

def main():
    spark = SparkSession.builder \
        .appName("SmartBiteAnalytics-DemandAnalysis") \
        .master("local[*]") \
        .getOrCreate()
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    csv_file = os.path.join(project_root, "data", "processed", "cleaned_orders.csv")
    output_dir = os.path.join(project_root, "data", "output")
    
    orders_df = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_file)
    
    demand_by_day = orders_df.groupBy("day_of_the_week") \
        .agg(
            count("order_id").alias("total_orders"),
            avg("cost_of_the_order").alias("avg_order_value"),
            sum("cost_of_the_order").alias("total_revenue")
        ) \
        .orderBy(col("total_orders").desc()) \
        .toPandas()
        
    demand_by_cuisine = orders_df.groupBy("cuisine_type") \
        .agg(
            count("order_id").alias("total_orders"),
            avg("cost_of_the_order").alias("avg_order_value"),
            avg("delivery_time").alias("avg_delivery_time")
        ) \
        .orderBy(col("total_orders").desc()) \
        .toPandas()
        
    demand_by_day.to_csv(os.path.join(output_dir, "demand_by_day.csv"), index=False)
    demand_by_cuisine.to_csv(os.path.join(output_dir, "demand_by_cuisine.csv"), index=False)
    
    print("[OK] Demand analysis completed.")
    spark.stop()

if __name__ == "__main__":
    main()