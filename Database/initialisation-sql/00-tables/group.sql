--  Drop table

--  DROP TABLE teh6_2019_summer_project.`group`;

CREATE TABLE teh6_2019_summer_project.`group` (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	min_credits INT(3) UNSIGNED NOT NULL,
	max_credits INT(3) UNSIGNED NULL,
	min_grade TINYINT(2) UNSIGNED NOT NULL,
	max_grade TINYINT(2) UNSIGNED NULL,
	requirement_id INT UNSIGNED NOT NULL,	-- the requirement the group belongs to
	CONSTRAINT group_PK PRIMARY KEY (id),
	CONSTRAINT group_requirement_FK FOREIGN KEY (requirement_id) REFERENCES teh6_2019_summer_project.requirement(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT group_credit_range CHECK (IFNULL((min_credits <= max_credits), 1)),	-- if max_credits is not NULL, check; else return 1 (true)
	CONSTRAINT group_grade_range CHECK (IFNULL((min_grade <= max_grade), 1))	-- if max_grade is not NULL, check; else return 1 (true)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
