--  Drop table

--  DROP TABLE teh6_2019_summer_project.programme_school;

CREATE TABLE teh6_2019_summer_project.programme_school (
	school_id INT UNSIGNED NOT NULL,
	programme_id INT UNSIGNED NOT NULL,
	CONSTRAINT programme_school_PK PRIMARY KEY (school_id,programme_id),
	CONSTRAINT programme_school_school_FK FOREIGN KEY (school_id) REFERENCES teh6_2019_summer_project.school(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT programme_school_programme_FK FOREIGN KEY (programme_id) REFERENCES teh6_2019_summer_project.programme(id) ON DELETE RESTRICT ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
