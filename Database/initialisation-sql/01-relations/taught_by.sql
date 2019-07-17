--  Drop table

--  DROP TABLE teh6_2019_summer_project.taught_by;

CREATE TABLE teh6_2019_summer_project.taught_by (
	module_code varchar(6) NOT NULL,
	lecturer_uname varchar(127) NOT NULL,
	academic_year varchar(9) NOT NULL,
	semester_number TINYINT(1) UNSIGNED NOT NULL,
	CONSTRAINT taught_by_PK PRIMARY KEY (module_code,lecturer_uname,academic_year,semester_number),
	CONSTRAINT taught_by_module_FK FOREIGN KEY (module_code) REFERENCES teh6_2019_summer_project.module(code) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT taught_by_lecturer_FK FOREIGN KEY (lecturer_uname) REFERENCES teh6_2019_summer_project.lecturer(user_name) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT taught_by_semester_FK FOREIGN KEY (semester_number) REFERENCES teh6_2019_summer_project.semester(`number`) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT taught_by_academic_year_FK FOREIGN KEY (academic_year) REFERENCES teh6_2019_summer_project.academic_year(title) ON DELETE RESTRICT ON UPDATE RESTRICT
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
