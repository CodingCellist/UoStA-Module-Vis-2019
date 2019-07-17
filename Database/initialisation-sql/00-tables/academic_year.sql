--  Drop table

--  DROP TABLE teh6_2019_summer_project.academic_year;

CREATE TABLE teh6_2019_summer_project.academic_year (
	title varchar(9) NOT NULL,
	CONSTRAINT academic_year_PK PRIMARY KEY (title),
	CONSTRAINT academic_year_format CHECK (title REGEXP '^[0-9]{4}-[0-9]{4}$')
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
