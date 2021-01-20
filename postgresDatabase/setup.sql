CREATE DATABASE course_moniter;

\c course_moniter

CREATE TABLE courses(
	id serial PRIMARY KEY,
	dept TEXT,
	course TEXT,
	section TEXT,
	campus TEXT,
	status TEXT
);

CREATE TABLE stats(
	stat TEXT PRIMARY KEY,
	value TEXT
);

INSERT INTO stats(stat, value) VALUES ('last_check', 0);