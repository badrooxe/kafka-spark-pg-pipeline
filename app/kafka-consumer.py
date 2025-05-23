# from kafka import KafkaConsumer
# import json

# consumer = KafkaConsumer(
#     'sensor-data',
#     bootstrap_servers='kafka:9092',
#     auto_offset_reset='earliest',
#     group_id='sensor-group',
#     value_deserializer=lambda m: json.loads(m.decode('utf-8'))
# )

# print("Starting consumer...")

# for message in consumer:
#     data = message.value
#     print(f"Received: {data}")

from pyspark.sql.types import StructType, StringType, IntegerType, DoubleType
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json

schema = StructType() \
    .add("country", StringType()) \
    .add("cases", IntegerType()) \
    .add("todayCases", IntegerType()) \
    .add("deaths", IntegerType()) \
    .add("todayDeaths", IntegerType()) \
    .add("recovered", IntegerType()) \
    .add("todayRecovered", IntegerType()) \
    .add("active", IntegerType()) \
    .add("critical", IntegerType()) \
    .add("casesPerOneMillion", DoubleType()) \
    .add("deathsPerOneMillion", DoubleType()) \
    .add("tests", IntegerType()) \
    .add("testsPerOneMillion", DoubleType()) \
    .add("population", IntegerType()) \
    .add("continent", StringType()) \
    .add("date", StringType())

session = SparkSession.builder \
    .appName("Covid Kafka Consumer") \
    .getOrCreate()

df_raw = session.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "covid-countries") \
    .option("startingOffsets", "latest") \
    .load()

df_json = df_raw.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

print("covid data : ", df_json)

def foreach_batch_function(df, epoch_id):
    try:
        # Debug print for structure
        print("=== Batch Schema ===")
        df.printSchema()
        print("=== Sample Data ===")
        df.show(5)

        # write to PostgreSQL
        try:
            df.write \
                .format("jdbc") \
                .option("url", "jdbc:postgresql://big-data-project-postgres-1:5432/covid_data") \
                .option("dbtable", "covid_stats") \
                .option("user", "sparkuser") \
                .option("password", "sparkpass") \
                .option("driver", "org.postgresql.Driver") \
                .mode("append") \
                .save()
            print("=== Data Written to PostgreSQL ===")
        except Exception as write_err:
            import traceback
            print(f"ERROR during DataFrame write: {write_err}")
            traceback.print_exc()

    except Exception as e:
        import traceback
        print(f"ERROR in foreach_batch_function: {e}")
        traceback.print_exc()


# Write to PostgreSQL in micro-batches
# query = df_json.writeStream \
#     .foreachBatch(lambda batch_df, batch_id: batch_df.write
#         .format("jdbc")
#         .option("url", "jdbc:postgresql://postgres:5432/covid_data")
#         .option("dbtable", "covid_stats")
#         .option("user", "sparkuser")
#         .option("password", "sparkpass")
#         .option("driver", "org.postgresql.Driver")
#         .mode("append")
#         .save()) \
#     .outputMode("append") \
#     .option("checkpointLocation", "/app/checkpoints/covid") \
#     .start()

query = df_json.writeStream \
    .foreachBatch(foreach_batch_function) \
    .outputMode("append") \
    .option("checkpointLocation", "/app/checkpoints/covid") \
    .start()

query.awaitTermination()

