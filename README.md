# SASA Database
I don't think this is usable by anyone lese but it's a dependency to `sasa_stacker` and I wanted to package it separately. An explanation to the whole project can be found [here](https://github.com/TimLucaTuran/bachlor-arbeit/blob/master/bachlor-arbeit.pdf).

## Usage
`exl_to_sql.py -h`:
<pre><code>
exl_to_sql.py [-h] [-n SHEET_NUMBER] [-v] [-s] exl db

positional arguments:
  exl                   path to excel-file
  db                    path to sqlite3-db


optional arguments:
  -h, --help            show this help message and exit
  -n SHEET_NUMBER, --sheet-number SHEET_NUMBER
                        which excel-sheet to convert
  -v, --verbose         verbose output
  -s, --skip-existing   skipping rows already contained in the db
</code></pre>

Writes the excel file `exl` into the sqlite database `db`. Every row in the Excel sheet represents one simulation run of metasurfaces. The problem is with our current setup they are saved as one big `.mat` file but the `sasa_stacker` needs to access them and their parameters individually. This script assigns each single metasurface an address and saves its parameters in the db separately. Examples for the formating of the excel sheet can be found in `data/NN_smats.xlsx`.

## Crawler
The Crawler class allows access to the db and loads the simulation data. The main functions are:


### find_smat

```python
Crawler.find_smat(name, adress=None)
```
Loads the simulation data to `name`. If an adress is provided it only loads this single S-matrix.

__Arguments__

- __name__: string, name of the simulation in the database
- __adress__: list, for example `[1,4,5,3]` the adress can also be found in the database

----

### find_smat_by_id

```python
Crawler.find_smat_by_id(id)
```
Same as above but takes the simulation id


__Arguments__

- __id__: int, simulation id found in the database

----

### extract_params

```python
Crawler.extract_params(id)
```
Queries meta_materials.db for all the parameters to the given ID.

__Arguments__

- __id__: int, simulation id found in the database


__Returns__
- __param_dict__: dict, contains the combined data from the simulations and geometry tables with coresponding names

----
