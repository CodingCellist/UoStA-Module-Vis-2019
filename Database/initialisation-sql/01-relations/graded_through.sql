--  Drop table

--  DROP TABLE teh6_2019_summer_project.graded_through;

CREATE TABLE teh6_2019_summer_project.graded_through (
	module_code varchar(6) NOT NULL,
	assessment_type varchar(63) NOT NULL,
	academic_year varchar(9) NOT NULL,
	percentage TINYINT(3) UNSIGNED NOT NULL,
	CONSTRAINT graded_through_PK PRIMARY KEY (module_code,assessment_type,academic_year),
	CONSTRAINT graded_through_module_FK FOREIGN KEY (module_code) REFERENCES teh6_2019_summer_project.module(code) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT graded_through_assessment_FK FOREIGN KEY (assessment_type) REFERENCES teh6_2019_summer_project.assessment(`type`) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT graded_through_academic_year_FK FOREIGN KEY (academic_year) REFERENCES teh6_2019_summer_project.academic_year(title) ON DELETE RESTRICT ON UPDATE RESTRICT
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
