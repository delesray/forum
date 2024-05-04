USE `forum` ;
-- -----------------------------------------------------
-- ADDITIONAL SEED
-- -----------------------------------------------------
-- INSERTING USERS
INSERT INTO users(username,password,email,is_admin) VALUES('admin', '$2b$12$snZATHX9lsgnazHFCtW1tuU9FYuGOnQlwKBeTFmIjx3Y.RZF0MNCS', 'admin@gmail.com', true);
INSERT INTO users(username,password,email,is_admin) VALUES('miray', '$2b$12$GCdLa2cgCgP4g3jSM8NLC.rRqU0vCfSYRhydsMlu7886uLBzwb0fm', 'miray@gmail.com', false);
INSERT INTO users(username,password,email,is_admin) VALUES('deni', '$2b$12$bKrSNwXIXc.vm9J9tVoAQOu4acqB/U.CfnqLgzm1b5GVZlZC51Zc6', 'deni@gmail.com', false);
INSERT INTO users(username,password,email,is_admin) VALUES('olesya', '$2b$12$QhENABDctn1WoWv3L3JDgOPZgZU/GVHcBZxYOI10Knr/idoInVDzy', 'olesya@gmail.com', false);
INSERT INTO users(username,password,email,is_admin) VALUES('random', '$2b$12$P4LdpTI4eRL2/b/wlXvLk.u1EfS.uACP6W98wK49Wf3vBN2Tgz7d2', 'random@gmail.com', false);

-- INSERTING CATEGORIES
INSERT INTO categories(name) VALUES('Uncategorized');
INSERT INTO categories(name) VALUES('Animals');
INSERT INTO categories(name) VALUES('Technology');
INSERT INTO categories(name) VALUES('Nature');
INSERT INTO categories(name) VALUES('Hobbies');
INSERT INTO categories(name, is_private) VALUES('FishingPrivate', 1);

-- INSERTING TOPICS
INSERT INTO topics(title,user_id,category_id) VALUES('I love my cat', 4,2);
INSERT INTO topics(title,user_id,category_id) VALUES('My dog is cool', 4,2);

INSERT INTO topics(title,user_id,category_id) VALUES('My laptop is Mac', 3,3);
INSERT INTO topics(title,user_id,category_id) VALUES('What computer to buy', 3,3);

INSERT INTO topics(title,user_id,category_id) VALUES('Volleyball is the best sport', 2,5);
INSERT INTO topics(title,user_id,category_id) VALUES('Snowboard?', 2,5);
INSERT INTO topics(title,user_id,category_id) VALUES('I love movies', 3,5);
INSERT INTO topics(title,user_id,category_id) VALUES('Suggest books', 3,5);
INSERT INTO topics(title,user_id,category_id) VALUES('Anyone coding in python?', 4,5);

-- private topic
INSERT INTO topics(title,user_id,category_id) VALUES('Where to go fishing?', 2,6);

-- INSERTING PERMISSIONS
INSERT INTO users_categories_permissions(user_id,category_id) VALUES(3,6);
INSERT INTO users_categories_permissions(user_id,category_id,write_access) VALUES(4, 6, 1);

-- INSERTING REPLIES
INSERT INTO replies(text,user_id,topic_id) VALUES('By the river',4, 9);
INSERT INTO replies(text,user_id,topic_id) VALUES('Ok that is a good idea',2, 9);
INSERT INTO replies(text,user_id,topic_id) VALUES('I caught some big fish there!!!',4, 9);


