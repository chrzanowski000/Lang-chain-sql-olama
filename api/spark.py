# api/spark.py
import os
from dotenv import load_dotenv
load_dotenv()

from pyspark.sql import SparkSession

SPARK_APP_NAME = os.getenv("SPARK_APP_NAME", "sql_rag_spark")
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
SPARK_DRIVER_MEM = os.getenv("SPARK_DRIVER_MEM", "6g")
SPARK_SQL_SHUFFLE_PARTITIONS = os.getenv("SPARK_SQL_SHUFFLE_PARTITIONS", "8")

_spark = None

def get_spark_session():
    global _spark
    if _spark is None:
        _spark = (
            SparkSession.builder
            .appName(SPARK_APP_NAME)
            .master(SPARK_MASTER)
            .config("spark.driver.memory", SPARK_DRIVER_MEM)
            .config("spark.sql.shuffle.partitions", SPARK_SQL_SHUFFLE_PARTITIONS)
            .getOrCreate()
        )
    return _spark
