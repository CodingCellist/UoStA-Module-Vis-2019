-- a couple of modules, just to be able to fill in the anti-requisites

CALL teh6_2019_summer_project.create_catalogue_entry(
	'PY4612', 'Advanced Logic', '2019-2020', 30, 2, "The module presupposes facility in the elementary practice of logic provided by PY2001/PY2010. This module makes use of meta-theoretical techniques to make logic itself the subject of formal investigation. The main goals of the module will be to tackle the standard metatheoretical results: completeness, compactness, the Lowenheim-Skolem theorems, and G÷del's celebrated incompleteness theorems. Along the way, there will be preparatory discussion of elementary set theory, model theory, and recursion theory.", TRUE
);
CALL teh6_2019_summer_project.create_catalogue_entry(
	'MT3852', 'Automata, Languages and Complexity', '2018-2019', 15, 2, "This module begins with finite state machines, context-free grammars and big-O notation. Turing machines, non-determinism and pushdown automata are introduced, followed by studies on decidability, simulation and the Halting problem. The complexity classes P, NP, co-NP, NP-hard, etc., are described via analysis of SAT and graph isomorphism. Strengths and limitations of the abstract approach to complexity are discussed, followed by an introduction to practical complexity.", TRUE
);
CALL teh6_2019_summer_project.create_catalogue_entry(
	'IS5108', 'Information Technology Projects', '2018-2019', 15, 2, "This module reinforces information technology and project management skills gained during semester 1, by means of a selection of coursework assignments posed as information technology projects. These are designed to offer increasing depth and scope for creativity as the module progresses.", FALSE
);
CALL teh6_2019_summer_project.create_catalogue_entry(
	'IS5108', ' Information Technology Projects', '2019-2020', 15, 2, "This module reinforces information technology and project management skills gained during semester 1, by means of a selection of coursework assignments posed as information technology projects. These are designed to offer increasing depth and scope for creativity as the module progresses.", FALSE
);
CALL teh6_2019_summer_project.create_id_module(
	'School of Mathematics and Statistics', 'ID5059', 'Knowledge Discovery and Datamining', '2018-2019', 15, 2, "Contemporary data collection can be automated and on a massive scale e.g. credit card transaction databases. Large databases potentially carry a wealth of important information that could inform business strategy, identify criminal activities, characterise network faults etc. These large scale problems may preclude the standard carefully constructed statistical models, necessitating highly automated approaches. This module covers many of the methods found under the banner of Datamining, building from a theoretical perspective but ultimately teaching practical application. Topics covered include: historical/philosophical perspectives, model selection algorithms and optimality measures, tree methods, bagging and boosting, neural nets, and classification in general. Practical applications build sought-after skills in programming (typically R, SAS or python).", TRUE
);
INSERT INTO teh6_2019_summer_project.taught_in
VALUES
('ID5059', 2, '2019-2020');
