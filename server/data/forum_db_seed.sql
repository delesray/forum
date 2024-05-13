USE `forum` ;
-- -----------------------------------------------------
-- ADDITIONAL SEED
-- -----------------------------------------------------
-- INSERTING USERS
INSERT INTO users(username,password,email,is_admin) -- 1
VALUES('admin', '$2b$12$snZATHX9lsgnazHFCtW1tuU9FYuGOnQlwKBeTFmIjx3Y.RZF0MNCS', 'admin@gmail.com', true);
INSERT INTO users(username,password,email,is_admin) -- 2
VALUES('miray', '$2b$12$GCdLa2cgCgP4g3jSM8NLC.rRqU0vCfSYRhydsMlu7886uLBzwb0fm', 'miray@gmail.com', false);
INSERT INTO users(username,password,email,is_admin) -- 3
VALUES('deni', '$2b$12$bKrSNwXIXc.vm9J9tVoAQOu4acqB/U.CfnqLgzm1b5GVZlZC51Zc6', 'deni@gmail.com', false);
INSERT INTO users(username,password,email,is_admin) -- 4
VALUES('olesya', '$2b$12$QhENABDctn1WoWv3L3JDgOPZgZU/GVHcBZxYOI10Knr/idoInVDzy', 'olesya@gmail.com', false);
INSERT INTO users(username,password,email,is_admin) -- 5
VALUES('random', '$2b$12$P4LdpTI4eRL2/b/wlXvLk.u1EfS.uACP6W98wK49Wf3vBN2Tgz7d2', 'random@gmail.com', false);

-- INSERTING CATEGORIES
INSERT INTO categories(name) VALUES('Uncategorized');-- 1
INSERT INTO categories(name) VALUES('Animals');-- 2
INSERT INTO categories(name) VALUES('Technology');-- 3
INSERT INTO categories(name) VALUES('Nature');-- 4
INSERT INTO categories(name) VALUES('Hobbies');-- 5
INSERT INTO categories(name, is_private) VALUES('FishingPrivate', 1);-- 6 private

-- INSERTING TOPICS
INSERT INTO topics(title,user_id,category_id) VALUES('I love my cat', 4,2);-- 1
INSERT INTO topics(title,user_id,category_id) VALUES('My dog is cool', 4,2);-- 2

INSERT INTO topics(title,user_id,category_id) VALUES('My laptop is Mac', 3,3);-- 3
INSERT INTO topics(title,user_id,category_id) VALUES('What computer to buy', 3,3);-- 4

INSERT INTO topics(title,user_id,category_id) VALUES('Volleyball is the best sport', 2,5);-- 5
INSERT INTO topics(title,user_id,category_id) VALUES('Snowboard?', 2,5);-- 6
INSERT INTO topics(title,user_id,category_id) VALUES('I love movies', 3,5);-- 7
INSERT INTO topics(title,user_id,category_id) VALUES('Suggest books', 3,5);-- 8
INSERT INTO topics(title,user_id,category_id) VALUES('Anyone coding in python?', 4,5);-- 9

INSERT INTO topics(title,user_id,category_id) VALUES('Where to go fishing?', 2,6);-- 10 private

-- INSERTING PERMISSIONS
INSERT INTO users_categories_permissions(user_id,category_id) VALUES(3,6); -- readonly
INSERT INTO users_categories_permissions(user_id,category_id,write_access) VALUES(4, 6, 1);-- write

-- INSERTING REPLIES
INSERT INTO replies(text,user_id,topic_id) VALUES('By the river',4, 10); -- 1
INSERT INTO replies(text,user_id,topic_id) VALUES('Ok that is a good idea',2, 10);-- 2
INSERT INTO replies(text,user_id,topic_id) VALUES('I caught some big fish there!!!',4, 10);-- 3

INSERT INTO replies(text,user_id,topic_id) VALUES('Good luck!',2, 3);
INSERT INTO replies(text,user_id,topic_id) VALUES('Do you like it!',2, 3);
INSERT INTO replies(text,user_id,topic_id) VALUES('The best!',2, 3);

-- INSERT INTO messages(text,sender_id,receiver_id) VALUES('done',1, 2);
-- INSERT INTO users_categories_permissions(user_id,category_id,write_access) VALUES(2, 6,1);