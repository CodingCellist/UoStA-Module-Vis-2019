--  Drop table

--  DROP TABLE teh6_2019_summer_project.requisite;

CREATE TABLE teh6_2019_summer_project.requisite (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	academic_year varchar(9) NOT NULL,
	semester_number TINYINT(1) UNSIGNED NOT NULL,
	academic_level varchar(3) NOT NULL,
	`type` varchar(4) NOT NULL,
	source_module varchar(6) NOT NULL,
	CONSTRAINT requisite_PK PRIMARY KEY (id),
	CONSTRAINT requisite_academic_year_FK FOREIGN KEY (academic_year) REFERENCES teh6_2019_summer_project.academic_year(title) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT requisite_semester_number_FK FOREIGN KEY (semester_number) REFERENCES teh6_2019_summer_project.semester(`number`) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT requisite_source_module_FK FOREIGN KEY (source_module) REFERENCES teh6_2019_summer_project.module(code) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT level_is_ug_pgt_pgr CHECK (academic_level IN ('UG', 'PGT', 'PGR')),
	CONSTRAINT type_is_pre_anti_co CHECK (`type` IN ('Pre', 'Anti', 'Co'))
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
