SELECT
	s.name AS `SchoolName`,
	ti.academic_year,
	ti.semester_number,
	m.code AS `ModuleCode`,
	m.name AS `ModuleName`,
	m.credit_worth AS `ModuleSCOTCATCredits`,
	m.re_assessable AS `IsReassessable`,
	m.description AS `ModuleDescription`
FROM module AS m
JOIN taught_in AS ti
ON ti.module_code = m.code
JOIN school AS s
ON m.school_id = s.id;