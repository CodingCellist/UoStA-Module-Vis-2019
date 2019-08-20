--  Drop table

--  DROP TABLE teh6_2019_summer_project.taught_through;

CREATE TABLE teh6_2019_summer_project.taught_through (
	module_code varchar(6) NOT NULL,
	teaching_type varchar(63) NOT NULL,
	hours SMALLINT(3) UNSIGNED NOT NULL,
	academic_year varchar(9) NOT NULL,
	CONSTRAINT taught_through_PK PRIMARY KEY (module_code,teaching_type,academic_year),
	CONSTRAINT taught_through_module_FK FOREIGN KEY (module_code) REFERENCES teh6_2019_summer_project.module(code) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT taught_through_teaching_FK FOREIGN KEY (teaching_type) REFERENCES teh6_2019_summer_project.teaching(`type`) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT taught_through_academic_year_FK FOREIGN KEY (academic_year) REFERENCES teh6_2019_summer_project.academic_year(title) ON DELETE RESTRICT ON UPDATE RESTRICT
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
