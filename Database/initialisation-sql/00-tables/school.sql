--  Drop table

--  DROP TABLE teh6_2019_summer_project.school;

CREATE TABLE teh6_2019_summer_project.school (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	name varchar(127) NOT NULL,
	CONSTRAINT school_PK PRIMARY KEY (id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
