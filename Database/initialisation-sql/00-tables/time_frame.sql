--  Drop table

--  DROP TABLE teh6_2019_summer_project.time_frame;

CREATE TABLE teh6_2019_summer_project.time_frame (
	module_code varchar(6) NOT NULL,
	`start` DATE NOT NULL,
	`end` DATE NOT NULL,
	CONSTRAINT time_frame_PK PRIMARY KEY (module_code,`start`,`end`),
	CONSTRAINT time_frame_module_FK FOREIGN KEY (module_code) REFERENCES teh6_2019_summer_project.module(code) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT time_frame_valid CHECK (`start` < `end`)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
