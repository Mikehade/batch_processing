# batch_processing
Designing a batch processing data pipeline for processing data using docker, spark and cassandra

## Steps to run batch processing

- pull repository
- open command prompt
- cd to batch_processing
- execute command **docker-compose up -d**  (One might have to add the path to the folder in the filesharing docker settings)
- execute command **docker ps** to view containers and corresponding id's

#### Launch cassandra cluster
- copy cassandra container id from listed containers after previous command
- execute command **docker exec -it container_id bash**
- change directory to 
- - 
