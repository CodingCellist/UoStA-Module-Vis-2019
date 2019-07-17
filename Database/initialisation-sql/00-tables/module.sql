--  Drop table

--  DROP TABLE teh6_2019_summer_project.module;

CREATE TABLE teh6_2019_summer_project.module (
	code varchar(6) NOT NULL,
	name varchar(255) NOT NULL,
	description varchar(2047) NOT NULL,
	credit_worth INT(3) UNSIGNED NOT NULL,
	re_assessable BOOL NOT NULL,
	external_requirement TEXT NULL,		-- any other requirements, e.g. A-levels
	school_id INT UNSIGNED NOT NULL,	-- the school that offers the module
	CONSTRAINT module_PK PRIMARY KEY (code),
	CONSTRAINT module_school_FK FOREIGN KEY (school_id) REFERENCES teh6_2019_summer_project.school(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT module_format CHECK (code REGEXP '^[A-Z]{2}[0-9]{4}$')
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
