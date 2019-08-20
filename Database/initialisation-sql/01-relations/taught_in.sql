--  Drop table

--  DROP TABLE teh6_2019_summer_project.taught_in;

CREATE TABLE teh6_2019_summer_project.taught_in (
	module_code varchar(6) NOT NULL,
	semester_number TINYINT(1) UNSIGNED NOT NULL,
	academic_year varchar(9) NOT NULL,
	CONSTRAINT taught_in_PK PRIMARY KEY (module_code,semester_number,academic_year),
	CONSTRAINT taught_in_module_FK FOREIGN KEY (module_code) REFERENCES teh6_2019_summer_project.module(code) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT taught_in_semester_FK FOREIGN KEY (semester_number) REFERENCES teh6_2019_summer_project.semester(`number`) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT taught_in_academic_year_FK FOREIGN KEY (academic_year) REFERENCES teh6_2019_summer_project.academic_year(title) ON DELETE RESTRICT ON UPDATE RESTRICT
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
