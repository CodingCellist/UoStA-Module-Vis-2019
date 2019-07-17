--  Drop table

--  DROP TABLE teh6_2019_summer_project.prefix;

CREATE TABLE teh6_2019_summer_project.prefix (
	code varchar(2) NOT NULL,
	school_id INT UNSIGNED NOT NULL,
	CONSTRAINT prefix_PK PRIMARY KEY (code),
	CONSTRAINT prefix_school_FK FOREIGN KEY (school_id) REFERENCES teh6_2019_summer_project.school(id) ON DELETE RESTRICT ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
