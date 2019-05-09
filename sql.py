import mysql.connector as mc
import os, sys
import openpyxl

mydb = mc.connect(
    host = "localhost",
    user = "root",
    passwd = "tltit69z",
    database = "meta_materials",
)
my_cursor = mydb.cursor()
wb = openpyxl.load_workbook("project_overview.xlsx")
sheets = wb.sheetnames
ws = wb[sheets[-8]]
my_cursor.execute("TRUNCATE TABLE simulations;")
my_cursor.execute("TRUNCATE TABLE wire;")
my_cursor.execute("TRUNCATE TABLE square;")



sql_dict={ 'geometry': None ,
           'm_file': None ,
           'particle_material': None ,
           'cladding': None ,
           'substrate': None ,
           'periode': None ,
           'wavelength_start': None ,
           'wavelength_stop': None ,
           'spectral_points': None ,
           'simulation_order': None ,
           'adress': None ,
           'length': None ,
           'width': None ,
           'thickness': None ,
           'corner_radius': None ,
           'radius': None ,
           'rounded_corner': None ,
           'hole': None,
           'simulation_id': None ,
          }


class Exl:
#Define the Excel-Struct it holds information of a Excel-Cell and which
#opperations need to be applied. For example the wavelength excel cell:
#"0.64 ... 1.7" needs to be split into wavelength_start and _stop
    def __init__(self, name, target_key, opperation_list=[]):
        self.name = name
        self.target_key = target_key
        self.opperation_list = opperation_list
        self.column = None
        self.data = None
        self.target_dict = sql_dict

    def write(self):
        self.target_dict[self.target_key] = self.data
        return


    def wav_split(self):
        try:
            start = float(self.data[:4].strip())
            stop = float(self.data[-4:].strip())
        except:
            raise RuntimeError(
                  "Failed to wav_split: {}".format(self.data))
        #copy stop to the SQL list, start will be taken care of by write()
        self.target_dict['wavelength_stop'] = stop
        self.data = start
        return

    def evaluate(self):
        try:
            self.data = float(eval(self.data))
        except:
            pass
        return

    def listify(self):
        """
        Some Excel Cells have Values like [5 7 9 11] or matlab like
        25:5:75. This method needs to turn these into python lists.
        """
        if type(self.data) is str:
            if ':' in self.data:
                nums = self.data.split(':')
                nums = [int(i) for i in nums]
                if len(nums) == 3:
                    start = nums[0]
                    step = nums[1]
                    stop = nums[2]
                elif len(nums) == 2:
                    start = nums[0]
                    step = 1
                    stop = nums[1]
                else:
                    raise ValueError('Weird number of ":" ')

                self.data = list(range(start, stop+step, step))

            elif '[' in self.data:
                self.data = self.data.replace('[', '').replace(']', '')
                self.data = self.data.replace(',', ' ').split()

            elif self.data.count(',') > 1:
                self.data = self.data.split(',')

        return

    def geo_setup(self):

        #check for additional geometry features
        if 'rounded' in self.data:
            self.target_dict['rounded_corner'] = 1

        if 'hole' in self.data:
            self.target_dict['hole'] = 1
        return




class QueryGenerator:
    def __init__(self, target_dict = sql_dict):
        self.target_dict = target_dict
        self.sim_query = 'INSERT INTO simulations ('
        self.geo_query = 'INSERT INTO '
        self.wire = ['simulation_id', 'length', 'width', 'thickness','corner_radius',
                    'rounded_corner']
        self.square = ['simulation_id', 'length', 'width', 'thickness', 'hole']
        self.geometries = {'wire' : self.wire,
                           'square' : self.square,
                           }
        self.adress = []

    def update_id(self):
        #get the current simulation_id
        my_cursor.execute("SELECT MAX(simulation_id) FROM simulations;")
        id = my_cursor.fetchone()[0]
        if id is None:
            id = 1
        else:
            id += 1
        print("ID: ", id)
        self.target_dict['simulation_id'] = id
        return

    def make_query(self, sql_dict):
        ###simulations query
        #consruct the list which holds the sql data to be submitted
        sim_data = []
        key_count = 0
        for key, val in sql_dict.items():
            if key == 'length':  #length is the first key for the geo-query
                break
            elif val is not None:
                sim_data.append(val)
                self.sim_query += key
                self.sim_query += ', '
                key_count += 1

        self.sim_query = self.sim_query[:-2]
        self.sim_query += ') VALUES ('
        self.sim_query += len(sim_data)* "%s, "
        self.sim_query = self.sim_query[:-2]
        self.sim_query += ')'

        #geometry query
        for geo in self.geometries:
            if geo in sql_dict['geometry']:
                sql_dict['geometry'] = geo
                self.geo_query += geo
                self.geo_query += ' ('
                current_geo = self.geometries[geo]
                break
        else:
            raise RuntimeError('Found no valid geometry in {}'.format(sql_dict['geometry']))

        #select the activ part of the dict for current geometry
        active_dict = [(key, val) for key, val in sql_dict.items() if key in current_geo]

        geo_data = []
        for key, val in active_dict:
            if sql_dict[key] is not None:
                geo_data.append(val)
                self.geo_query += key
                self.geo_query += ', '

        self.geo_query = self.geo_query[:-2]
        self.geo_query += ') VALUES ('
        self.geo_query += len(geo_data)*"%s, "
        self.geo_query = self.geo_query[:-2]
        self.geo_query += ')'
        print(self.sim_query)
        print(sim_data)
        print(len(sim_data),'=', key_count)
        print(self.geo_query)
        print(geo_data)
        print('\n')

        #Try to execute the queries
        try:
            my_cursor.execute(self.sim_query, tuple(sim_data))
        except Exception as e:
            print('Bad simulation query')
            print(e)

        self.update_id()
        try:
            my_cursor.execute(self.geo_query, tuple(geo_data))
        except Exception as e:
            print('Bad geometry query')
            print(e)

        self.sim_query = 'INSERT INTO simulations ('
        self.geo_query = 'INSERT INTO '

        return

    def loop_sql_dict(self, sql_dict, list_vals):
        if len(list_vals) == 0:
            print('adress: ', self.adress)
            self.make_query(sql_dict)
            return
        else:
            print('loop called')
            tup = list_vals.pop()
            current_key = tup[0]
            current_list = tup[1]
            self.adress.append(None)

            for i in range(len(current_list)):
                sql_dict[current_key] = current_list[i]
                self.adress[-1] = i
                sql_dict['adress'] = str(self.adress)
                self.loop_sql_dict(sql_dict, list_vals)

            #reset the adress

            sql_dict['adress'] = None
            return



    def generate(self, sql_dict):
        """
        This method gets a possibly nested sql_dict.
        It splits them up and calls make_query for every simple list.
        """
        #find the colums which have list-values
        list_vals = [(key, val) for key, val in sql_dict.items()
                    if type(val) is list]
        list_vals.sort(key = lambda tup : len(tup[1]), reverse = True)
        print('list_cols: ', list_vals)
        #reset the adress
        self.adress = []
        self.loop_sql_dict(sql_dict, list_vals)
        return



#Define the excel_list with one Exl for every column
#Setup ist Exl(excel_name, sql_name, [opperations])
exl_list = [Exl('m-file', 'm_file'),
            Exl('material', 'particle_material'),
            Exl('cladding', 'cladding'),
            Exl('substrate', 'substrate'),
            Exl('geom', 'geometry', [Exl.geo_setup]),
            Exl('periode', 'periode' ),
            Exl('wavelength', 'wavelength_start', [Exl.wav_split]),
            Exl('points', 'spectral_points'),
            Exl('order', 'simulation_order'),
            Exl('length', 'length', [Exl.evaluate, Exl.listify]),
            Exl('width', 'width', [Exl.evaluate, Exl.listify]),
            Exl('thickness', 'thickness', [Exl.evaluate, Exl.listify]),
            Exl('corner radius', 'corner_radius'),
            ]


####Read the excel data into the exl_list
#find the row with the column names
for row in ws.iter_rows():
    if 'file' in row[0].value:
        name_row = row

#find the position of each excel collumn
for cell in name_row:
    for exl in exl_list:
        if exl.name in cell.value and exl.column is None:
            exl.column = cell.column -1


####Main loop: Generate SQL-queries for every Excel row####
query_gen = QueryGenerator()
for row in ws.iter_rows(name_row[0].row + 1, ws.max_row):
    #Break on empty row
    if len(row[0].value) == 0:
        break
    #Load the data of the row
    print('row: ', row[0].row)
    for i in range(len(row)):
        for exl in exl_list:
            if i == exl.column:
                exl.data = row[i].value

    for exl in exl_list:
        for opperation in exl.opperation_list:
            opperation(exl)
        exl.write()

    query_gen.generate(sql_dict)

mydb.commit()
