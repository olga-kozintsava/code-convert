CREATE DATABASE code_convert;
CREATE ROLE admin WITH ENCRYPTED PASSWORD *****;
GRANT ALL PRIVILEGES ON DATABASE code_convert to admin;
ALTER ROLE admin WITH LOGIN;



CREATE TABLE Convert (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_user INT,
    in_file VARCHAR(200),
    out_file VARCHAR(200),
    in_file_loc INT,
    in_file_size INT,
    in_tmstmp TIMESTAMP,
    out_tmstmp TIMESTAMP,

    FOREIGN KEY (id_user)  REFERENCES User (id)
);


CREATE TABLE Account (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user INT,
    balance INT,

    FOREIGN KEY (user) REFERENCES User (id)
)