DROP TABLE IF EXISTS user;

DROP TABLE IF EXISTS log;

DROP TABLE IF EXISTS invite_code;

DROP TABLE IF EXISTS mods;

CREATE TABLE user(
    id TINYINT NOT NULL AUTO_INCREMENT,
    username VARCHAR(64)  NOT NULL,
    password VARCHAR(255) NOT NULL,
    level TINYINT DEFAULT 0,
    PRIMARY KEY(id),
    UNIQUE(username)
)ENGINE=InnoDB;

CREATE TABLE log(
id INT UNSIGNED NOT NULL AUTO_INCREMENT,
event VARCHAR(255) NOT NULL,
description TEXT NOT NULL,
admin_id TINYINT UNSIGNED NOT NULL REFERENCES user(id),
executed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY(id)
)ENGINE=InnoDB;

CREATE TABLE invite_code(
id INT UNSIGNED NOT NULL AUTO_INCREMENT,
code VARCHAR(255) NOT NULL,
created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
used_by VARCHAR(255) NOT NULL,
used BOOLEAN DEFAULT FALSE,
PRIMARY KEY(id),
UNIQUE(code)
)ENGINE=InnoDB;

CREATE TABLE mods(
    id TINYINT NOT NULL AUTO_INCREMENT,
    mod_id VARCHAR(64)  NOT NULL,
    mod_url VARCHAR(255) NOT NULL,
    mod_name VARCHAR(64)  NOT NULL,
    PRIMARY KEY(id),
    UNIQUE(mod_id)
)ENGINE=InnoDB;