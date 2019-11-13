import sqlite3
conn = sqlite3.connect('NN_smats.db')
c = conn.cursor()

with conn:
    c.execute("""CREATE TABLE simulations(
        simulation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        m_file TEXT,
        adress VARCHAR(30),
        particle_material VARCHAR(30),
        cladding VARCHAR(30),
        substrate VARCHAR(30),
        periode INT UNSIGNED,
        wavelength_start FLOAT,
        wavelength_stop FLOAT,
        spectral_points INT UNSIGNED,
        simulation_order INT UNSIGNED,
        geometry TEXT CHECK(geometry IN ('wire','square','disc','circ') ),
        angle_of_incidence INT DEFAULT 0)"""
        )

    c.execute("""CREATE TABLE square(
        simulation_id INT UNSIGNED PRIMARY KEY,
        width INT UNSIGNED,
        thickness INT UNSIGNED,
        hole TEXT DEFAULT 'no holes')"""
        )

    c.execute("""CREATE TABLE wire(
        simulation_id INT UNSIGNED PRIMARY KEY,
        length INT UNSIGNED,
        width INT UNSIGNED,
        thickness INT UNSIGNED,
        rounded_corner BOOL DEFAULT FALSE,
        corner_radius FLOAT,
        image_source VARCHAR(50) )"""
        )

    c.execute("""CREATE TABLE disc(
        simulation_id INT UNSIGNED PRIMARY KEY,
        radius INT UNSIGNED,
        height INT UNSIGNED,
        thickness INT UNSIGNED)"""
        )

    c.execute("""CREATE TABLE circ(
        simulation_id INT UNSIGNED PRIMARY KEY,
        width INT UNSIGNED,
        thickness INT UNSIGNED,
        hole BOOL DEFAULT FALSE)"""
        )

    c.execute("""CREATE TABLE L(
        simulation_id INT UNSIGNED PRIMARY KEY,
        length INT UNSIGNED,
        width INT UNSIGNED,
        thickness INT UNSIGNED,
        girth INT UNSIGNED)"""
        )
