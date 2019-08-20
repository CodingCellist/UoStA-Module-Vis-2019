--  Drop table

--  DROP TABLE teh6_2019_summer_project.timetable;

CREATE TABLE teh6_2019_summer_project.timetable (
	module_code varchar(6) NOT NULL,
	academic_year varchar(9) NOT NULL,
	url varchar(255) NOT NULL,
	CONSTRAINT timetable_PK PRIMARY KEY (module_code,academic_year,url),
	CONSTRAINT timetable_module_FK FOREIGN KEY (module_code) REFERENCES teh6_2019_summer_project.module(code) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT timetable_academic_year_FK FOREIGN KEY (academic_year) REFERENCES teh6_2019_summer_project.academic_year(title) ON DELETE RESTRICT ON UPDATE RESTRICT
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
