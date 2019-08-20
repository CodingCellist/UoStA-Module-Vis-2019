--  Drop table

--  DROP TABLE teh6_2019_summer_project.requisite_group;

CREATE TABLE teh6_2019_summer_project.requisite_group (
	group_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	requisite_id INT UNSIGNED NOT NULL,
	CONSTRAINT requisite_group_PK PRIMARY KEY (group_id),
	CONSTRAINT requisite_group_requirement_FK FOREIGN KEY (requisite_id) REFERENCES teh6_2019_summer_project.requisite(id) ON DELETE CASCADE ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
