CREATE USER pizzeria PASSWORD 'p';

CREATE DATABASE pizzeria;

GRANT ALL ON DATABASE pizzeria TO pizzeria;

CREATE TABLESPACE pizzeriaspace OWNER pizzeria LOCATION '/tablespace/pizzeria';
