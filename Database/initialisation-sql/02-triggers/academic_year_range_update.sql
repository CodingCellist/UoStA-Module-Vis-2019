CREATE TRIGGER academic_year_range_update
BEFORE UPDATE
ON academic_year FOR EACH ROW
BEGIN
	DECLARE year_start, year_end varchar(4);
	SET year_start = SUBSTRING(NEW.title FROM 1 FOR 4);
	SET year_end = SUBSTRING(NEW.title FROM -4);
	IF (CAST(year_end AS INT) - CAST(year_start AS INT)) != 1 THEN
		SIGNAL SQLSTATE '45001' SET message_text = "An academic year must span exactly one (1) year, e.g. 2018-2019.";
	END IF;
END