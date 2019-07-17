CREATE TRIGGER max_triple_honours_update
BEFORE UPDATE
ON programme_school FOR EACH ROW
BEGIN
	IF (SELECT COUNT(*) FROM programme_school WHERE programme_school.programme_id = NEW.programme_id) >= 3 THEN
		SIGNAL SQLSTATE '45001' SET message_text = "A programme cannot be offered by more than 3 schools.";
	END IF;
END