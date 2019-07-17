--  Drop table

--  DROP TABLE teh6_2019_summer_project.disjunctive_group;

CREATE TABLE teh6_2019_summer_project.disjunctive_group (
	group_id INT UNSIGNED NOT NULL,
	module_code varchar(6) NOT NULL,
	CONSTRAINT disjunctive_group_PK PRIMARY KEY (group_id,module_code),
	CONSTRAINT disjunctive_group_id_FK FOREIGN KEY (group_id) REFERENCES teh6_2019_summer_project.disjunctive_group(group_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT disjunctive_group_module_code_FK FOREIGN KEY (module_code) REFERENCES teh6_2019_summer_project.module(code) ON DELETE RESTRICT ON UPDATE RESTRICT
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
