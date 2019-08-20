--  Drop table

--  DROP TABLE teh6_2019_summer_project.module_group;

CREATE TABLE teh6_2019_summer_project.module_group (
	group_id INT UNSIGNED NOT NULL,
	module_code varchar(6) NOT NULL,
	CONSTRAINT module_group_PK PRIMARY KEY (group_id,module_code),
	CONSTRAINT module_group_group_FK FOREIGN KEY (group_id) REFERENCES teh6_2019_summer_project.`group`(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT module_group_module_FK FOREIGN KEY (module_code) REFERENCES teh6_2019_summer_project.module(code) ON DELETE RESTRICT ON UPDATE RESTRICT
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
