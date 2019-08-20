CREATE OR REPLACE
VIEW `complete_requisites` AS select
    `r`.`id` AS `RequisiteID`,
    `r`.`source_module` AS `source_module`,
    `r`.`academic_level` AS `academic_level`,
    `r`.`type` AS `type`,
    `r`.`academic_year` AS `academic_year`,
    `r`.`semester_number` AS `semester_number`,
    `dg`.`group_id` AS `DisjunctiveGroupID`,
    `dg`.`module_code` AS `TargetModule`
from
    ((`requisite` `r`
join `requisite_group` `rg` on
    (`r`.`id` = `rg`.`requisite_id`))
join `disjunctive_group` `dg` on
    (`rg`.`group_id` = `dg`.`group_id`))