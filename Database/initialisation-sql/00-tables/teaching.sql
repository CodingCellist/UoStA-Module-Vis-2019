--  Drop table

--  DROP TABLE teh6_2019_summer_project.teaching;

CREATE TABLE teh6_2019_summer_project.teaching (
	`type` varchar(63) NOT NULL,
	description varchar(511) NULL,
	CONSTRAINT teaching_PK PRIMARY KEY (`type`)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
