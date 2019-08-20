--  Drop table

--  DROP TABLE teh6_2019_summer_project.lecturer;

CREATE TABLE teh6_2019_summer_project.lecturer (
	user_name varchar(127) NOT NULL,
	title varchar(15) NOT NULL,
	first_name varchar(127) NOT NULL,
	surname varchar(127) NOT NULL,
	CONSTRAINT lecturer_PK PRIMARY KEY (user_name),
	CONSTRAINT lecturer_uname_format CHECK (user_name REGEXP '^[a-z]+[0-9]*$')
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
