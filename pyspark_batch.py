
    
import os
packages = ["pandas", "schedule", "cassandra-driver"]
for package in packages:
    #install(package)
    os.system(f'pip install {package}') 


import pandas as pd
import datetime
from datetime import datetime, timedelta
import time

from cassandra.cluster import Cluster
import schedule
import warnings
warnings.filterwarnings('ignore')


from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp
from pyspark.sql import functions as F
from pyspark.sql.types import *


def main():


    input_path = "input"
    output_path = "output"


    spark = SparkSession.builder.appName("answers").getOrCreate()


    path = f"{input_path}/iot_telemetry_data.csv"

    df = spark.read.option("header",'True').option('delimiter', ',').csv(path)
    #df.printSchema()





    df.show()


    df = df.withColumn("ts", col("ts").cast("float"))
    df.show()


    #df.printSchema()

    df = df.withColumn('ts', to_timestamp('ts').cast(DateType()))
    df.printSchema()

    df.show()

    
    cast_columns = ["co", "humidity", "lpg", "smoke", "temp"]
    for col_name in cast_columns:
        df = df.withColumn(col_name, col(col_name).cast('float'))
    df.printSchema()


    # Fill null values in numeric columns
    #for column in cast_columns:
        #df = df.withColumn(column, df[column].fillna(0))
        #df = df.withColumn(column, col(column).fillna(0))
    
    initial_data(df)
    
    
    spark.stop()




def mapred(dat, df):
    """
    Function to run map reduce
    
    this finction maps each device id to a specific dataframe
    after mapping to each dataframe, it is reduced by computing mean of dataframe grouped by date
    
    input: dataframe
    output: """
    #get unique sensor device ids into list
    uniq_dev = df.select('device').distinct().collect()
    uniq_dev = [d[-1] for d in uniq_dev]
    #print(uniq_dev)
    count = 0
    
    #for loop to map and reduce by unique device id
    for dev in uniq_dev:
        map_df = df.filter(df["device"] == dev)  #map using device id
        #display(map_df)
        
        #count true and false in light column
        lights = map_df.select('light').collect()
        lights = [l[-1] for l in lights]
        #lights
        l_true = 0
        l_false = 0
        for li in lights:
            if li == "true":
                l_true += 1
            elif li == "false":
                l_false += 1
        #print(l_true, l_false)
        
        #count distinct in motion
        motion = map_df.select('motion').collect()
        motion = [m[-1] for m in motion]
        #lights
        m_true = 0
        m_false = 0
        for mo in motion:
            if mo == "true":
                m_true += 1
            elif mo == "false":
                m_false += 1
        #print(m_true, m_false)
        
        
        
        rdf = map_df.groupBy("device").agg({'co':'avg', 'humidity':'avg', 'lpg':'avg', 'smoke':'avg'})
        #display(rdf.show())
        #rdf.printSchema()
        
        
        #group_df["device"] = dev    #assign device column
        
        device_id = rdf.select('device').collect()
        device_id = device_id[-1][-1]
        lpg = rdf.select('avg(lpg)').collect()
        lpg = lpg[-1][-1]
        smoke = rdf.select('avg(smoke)').collect()
        smoke = smoke[-1][-1]
        hum = rdf.select('avg(humidity)').collect()
        hum = hum[-1][-1]
        co = rdf.select('avg(co)').collect()
        co = co[-1][-1]
        print()
        print(f"Device ID: {device_id},\
        \n Date: {dat},\
        \n Lpg: {lpg},\
        \n Smoke: {smoke},\
        \n Humidity: {hum},\
        \n Co: {co},\
        \n light_true: {l_true},\
        \n light_false: {l_false},\
        \n motion_true: {m_true}, \
        \n motion_false: {m_false}")
        print()

        print("......Initializing Cassandra Cluster........")
        #['127.0.0.1'], port=9042
        cluster = Cluster(['cassandra'])  #127.0.0.1:9042   #['cassandra'] #
        session = cluster.connect()
        print(".......Connecting Cassandra Cluter........")
        print()

        print("........Executing create table cql query...........")
        session.execute("CREATE KEYSPACE IF NOT EXISTS batch WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 3}")
        session.execute("CREATE TABLE IF NOT EXISTS batch.sensors (device_id text PRIMARY KEY, date timestamp, \
                        lpg float, smoke float, humidity float, co float, \
                        light_true Boolean, light_false Boolean, motion_true Boolaen, \
                        motion_false Boolean)")
        #for r in result.collect():
        session.execute(f"INSERT INTO mykeyspace.mytable (device_id, date, lpg, smoke, humidity, co, \
                        light_true, light_false, motion_true, motion_false) VALUES \
                         ({device_id}, {dat}, {lpg}, {smoke}, {hum}, {co}, {l_true}, {l_false}, \
                        {m_true}, {m_false})")
        
       
    return rdf



    


def initial_data(df):

    uniq_date = df.select('ts').distinct().collect()
    #uniq_dev = df.select('device').distinct().rdd.flatMap(lambda x: x).collect()
    uniq_date = [d[-1] for d in uniq_date]

    for ds in uniq_date:  #iterate original dataset by date
        print(ds)
        #extract dataframe by date
        df_curr = df.filter(df["ts"] == ds)
        #display(df_curr)

        #extract reduced df by calling nap reduce function
        reduced_df = mapred(ds, df_curr)





main()


