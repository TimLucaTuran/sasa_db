/*
USE meta_materials;
CREATE TABLE simulations(
    simulation_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    m_file VARCHAR(70),
    particle_material VARCHAR(30),
    cladding VARCHAR(30),
    substrate VARCHAR(30),
    periode INT UNSIGNED,
    spectral_points INT UNSIGNED,
    simulation_order INT UNSIGNED,
);

CREATE TABLE square(
    simulation_id INT UNSIGNED PRIMARY KEY,
    length INT UNSIGNED,
    width INT UNSIGNED,
    thickness INT UNSIGNED,
    hole BOOL DEFAULT FALSE
);

CREATE TABLE square(
    simulation_id INT UNSIGNED PRIMARY KEY,
    width INT UNSIGNED,
    thickness INT UNSIGNED,
    hole BOOL DEFAULT FALSE
);


CREATE TABLE wire(
    simulation_id INT UNSIGNED PRIMARY KEY,
    length INT UNSIGNED,
    width INT UNSIGNED,
    thickness INT UNSIGNED,
    rounded_corner BOOL DEFAULT FALSE,
    corner_randius FLOAT
);
CREATE TABLE disc(
simulation_id INT UNSIGNED PRIMARY KEY,
radius INT UNSIGNED,
height INT UNSIGNED,
thickness INT UNSIGNED
);
ALTER TABLE wire ADD COLUMN rounded BOOLEAN;
ALTER TABLE simulations MODIFY substrate VARCHAR(30);
ALTER TABLE simulations MODIFY cladding VARCHAR(30);
ALTER TABLE simulations MODIFY geometry ENUM('wire', 'square', 'bar');
ALTER TABLE simulations MODIFY periode INT UNSIGNED;
ALTER TABLE simulations MODIFY m_file VARCHAR(50);
ALTER TABLE simulations MODIFY wav_len_start INT UNSIGNED;
ALTER TABLE simulations MODIFY wav_len_stop INT UNSIGNED;
ALTER TABLE simulations MODIFY spectral_points INT UNSIGNED;
ALTER TABLE simulations MODIFY simulation_order INT UNSIGNED;
*/
