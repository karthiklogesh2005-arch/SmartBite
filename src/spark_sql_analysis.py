import os
from pyspark.sql import SparkSession

os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"

def main():
    spark = SparkSession.builder \
        .appName("SmartBiteAnalytics-SparkSQL") \
        .master("local[*]") \
        .getOrCreate()
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    csv_file = os.path.join(project_root, "data", "processed", "cleaned_orders.csv")
    output_dir = os.path.join(project_root, "data", "output")
    
    orders_df = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_file)
    orders_df.createOrReplaceTempView("orders")
    
    top_restaurants = spark.sql("""
        SELECT restaurant_name, COUNT(order_id) as total_orders, ROUND(AVG(cost_of_the_order), 2) as avg_order_value
        FROM orders
        GROUP BY restaurant_name
        ORDER BY total_orders DESC
        LIMIT 10
    """).toPandas()
    
    top_restaurants.to_csv(os.path.join(output_dir, "top_restaurants_sql.csv"), index=False)
    
    print("[OK] Spark SQL analysis completed.")
    spark.stop()

if __name__ == "__main__":
    main()