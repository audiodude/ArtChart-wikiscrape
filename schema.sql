DROP TABLE IF EXISTS `artists`;
CREATE TABLE `artists` (
  `id` INT(10) UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  UNIQUE KEY (`name`)
) CHARACTER SET=utf8;

DROP TABLE IF EXISTS `locations`;
CREATE TABLE `locations` (
  `id` INT(10) UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  UNIQUE KEY (`name`)
) CHARACTER SET=utf8;

DROP TABLE IF EXISTS `works`;
CREATE TABLE `works` (
  `id` INT(10) UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `artist_id` INT(10) UNSIGNED,
  `location_id` INT(10) UNSIGNED,
  `url` VARCHAR(600),
  KEY `artist_id` (`artist_id`),
  KEY `location_id` (`location_id`),
  FOREIGN KEY (`artist_id`) REFERENCES `artists` (`id`),
  FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`)
) CHARACTER SET=utf8;