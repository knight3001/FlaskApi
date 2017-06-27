CREATE TABLE jobs (
 job_id integer PRIMARY KEY,
 add_date text NOT NULL,
 complete_date text NULL,
 detail text NULL
);

CREATE TABLE locations (
 location_id integer PRIMARY KEY,
 name text NOT NULL,
 address text NOT NULL,
 latitude real NULL,
 longitude real NULL
);

CREATE TABLE job_location (
 job_id integer,
 location_id integer,
 PRIMARY KEY (job_id, location_id),
 FOREIGN KEY (job_id) REFERENCES jobs (job_id) 
 ON DELETE CASCADE ON UPDATE NO ACTION,
 FOREIGN KEY (location_id) REFERENCES locations (location_id) 
 ON DELETE CASCADE ON UPDATE NO ACTION
);
