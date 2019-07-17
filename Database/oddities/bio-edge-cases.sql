-- BL-coded modules with requisite oddities


-- [x] BL2230 has duplicate pre-requisites
CALL teh6_2019_summer_project.create_pre_requisite('BL3320', 'BL2300', 'UG', '2019-2020', 1);

-- [ ] as far as I can tell, BL4225's anti-requisite (BL5420) has never existed...
-- CALL teh6_2019_summer_project.create_anti_requisite(BL4225, BL5420, UG, 2019-2020, 1);
CALL teh6_2019_summer_project.create_pre_requisite('BL4225', 'BL3303', 'UG', '2019-2020', 1);
CALL teh6_2019_summer_project.add_alt_pre_req_by_existing_pre_req('BL4225', 'BL3303', 'UG', '2019-2020', 1, 'BL3315');
