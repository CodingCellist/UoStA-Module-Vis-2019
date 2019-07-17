--  Drop table

--  DROP TABLE teh6_2019_summer_project.academic_level;

CREATE TABLE teh6_2019_summer_project.academic_level (
	acronym varchar(4) NOT NULL,
	name varchar(31) NOT NULL,
	CONSTRAINT academic_level_PK PRIMARY KEY (acronym)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
