--  Drop table

--  DROP TABLE teh6_2019_summer_project.requirement;

CREATE TABLE teh6_2019_summer_project.requirement (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	min_year_of_study TINYINT(1) UNSIGNED NOT NULL,
	max_year_of_study TINYINT(1) UNSIGNED NOT NULL,
	programme_id INT UNSIGNED NOT NULL,		-- the programme the requirement belongs to
	CONSTRAINT requirement_PK PRIMARY KEY (id),
	CONSTRAINT requirement_programme_FK FOREIGN KEY (programme_id) REFERENCES teh6_2019_summer_project.programme(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT requirement_year_range CHECK (min_year_of_study <= max_year_of_study)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
