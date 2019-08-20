--  Drop table

--  DROP TABLE teh6_2019_summer_project.programme;

CREATE TABLE teh6_2019_summer_project.programme (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	name varchar(127) NOT NULL,
	duration varchar(63) NOT NULL,
	`type` varchar(15) NOT NULL,
	CONSTRAINT programme_PK PRIMARY KEY (id),
	CONSTRAINT programme_type CHECK (`type` REGEXP '^Undergraduate$|^Postgraduate$|^Foundation$')
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
