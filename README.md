# batch_processing
Designing a batch processing data pipeline for processing data using docker, spark and cassandra

This pipeline reads data from a csv file, processes it and then save into a cassandra database

## Steps to run batch processing

- pull repository
- open command prompt
- cd to batch_processing
- execute command **docker-compose up -d**  (One might have to add the path to the folder in the filesharing docker settings)
- execute command **docker ps** to view containers and corresponding id's

#### Launch Cassandra cluster
- copy cassandra container id from listed containers after previous command
- execute command **docker exec -it cassandra_container_id bash**
- change directory to launch cqlsh by executing **cd opt/bitnami/cassandra/bin**
- wait a few minutes to allow time for connection to server then execute the following command **cqlsh -u cassandra -p cassandra**

#### Launch Spark
- open new command prompt
- change directory to batch_processing
- execute **docker ps** to view spark container id
- execute command **docker exec -it spark_container_id bash**
- change directory to /opt/spark using the following steps: - 
- - cd ..
- - cd ..
- - cd spark
- execute the following command to submit job **spark-submit pyspark_batch.py**

**exit** can be used to exit out of containers

Note: - I used a loop inside the pyspark file since I am simulating batch processing, otherwise I would use a scheduler like crontab or airflow.
