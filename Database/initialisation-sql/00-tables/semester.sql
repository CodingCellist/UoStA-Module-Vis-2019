--  Drop table

-- DROP TABLE teh6_2019_summer_project.semester;

CREATE TABLE teh6_2019_summer_project.semester (
	`number` TINYINT(1) UNSIGNED NOT NULL,
	name varchar(10) NOT NULL,
	start_month INT(2) UNSIGNED NOT NULL,
	end_month INT(2) UNSIGNED NOT NULL,
	CONSTRAINT semester_PK PRIMARY KEY (`number`),
	CONSTRAINT semester_number CHECK (`number` BETWEEN 1 AND 4),
	CONSTRAINT semester_name_type CHECK (name REGEXP 'Semester 1|Semester 2|Summer|Full Year'),
	CONSTRAINT semester_month_range CHECK ((start_month BETWEEN 1 AND 12) && (end_month BETWEEN 1 AND 12))
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
