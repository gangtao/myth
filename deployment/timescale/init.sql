DROP DATABASE IF EXISTS devops;
CREATE DATABASE devops;
CREATE USER test WITH PASSWORD 'test';
GRANT CONNECT ON DATABASE devops TO test;