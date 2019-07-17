--  Drop table

--  DROP TABLE teh6_2019_summer_project.assessment;

CREATE TABLE teh6_2019_summer_project.assessment (
	`type` varchar(63) NOT NULL,
	description TINYTEXT NULL,
	CONSTRAINT assessment_PK PRIMARY KEY (`type`)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
