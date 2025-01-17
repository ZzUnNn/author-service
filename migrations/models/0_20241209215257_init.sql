-- upgrade --
CREATE TABLE IF NOT EXISTS `user1` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `hashed_password` VARCHAR(255) NOT NULL,
    `id_number` VARCHAR(255),
    `username` VARCHAR(255) NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `loginhistory` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_agent` VARCHAR(255) NOT NULL,
    `timestamp` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `email` VARCHAR(255) NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_loginhis_user1_dce18a1d` FOREIGN KEY (`user_id`) REFERENCES `user1` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
