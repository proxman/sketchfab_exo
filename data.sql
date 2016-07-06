/*
-- Query: SELECT * FROM sketchfab_db.badgesfab_rule
LIMIT 0, 1000

-- Date: 2016-07-06 17:40
*/
INSERT INTO `badgesfab_rule` (`id`,`name`,`model_field`,`operator`,`value`,`content_type_id`) VALUES (3,'Star','users_views_count','__gt__','1000',13);
INSERT INTO `badgesfab_rule` (`id`,`name`,`model_field`,`operator`,`value`,`content_type_id`) VALUES (7,'Collector','models_per_uploader_count','__gt__','5',13);
INSERT INTO `badgesfab_rule` (`id`,`name`,`model_field`,`operator`,`value`,`content_type_id`) VALUES (8,'Pionneer','account_age','__gt__','0',11);
