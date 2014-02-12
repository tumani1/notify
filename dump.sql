CREATE TABLE user (
	userid int NOT NULL PRIMARY KEY,
	username varchar(20) NOT NULL,
	password varchar(50) NOT NULL,
);

INSERT INTO user VALUES (1, 'qwerty', '123456');
INSERT INTO user VALUES (2, 'qwerty1', '123456');
INSERT INTO user VALUES (3, 'qwerty2', '123456');
