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


#If you modify this list you might need to also modify QueryGenerator.make_query
sql_list=[['geometry', None],
          ['m_file', None],
          ['particle_material', None],
          ['cladding', None],
          ['substrate', None],
          ['periode', None],
          ['wavelength_start', None],
          ['wavelength_stop', None],
          ['spectral_points', None],
          ['simulation_order', None],
          ['adress', None],
          ['length', None],
          ['width', None],
          ['thickness', None],
          ['corner_radius', None],
          ['radius', None],
          ['rounded_corner', None],
          ['hole', None],
          ]

          #Define the Excel-Struct it holds information of a Excel-Cell and which
          #opperations need to be applied. For example the wavelength excel cell:
          #"0.64 ... 1.7" needs to be split into wavelength_start and _stop
class Exl:
    def __init__(self, name, target_pos, opperation_list=[]):
        self.name = name
        self.target_pos = target_pos
        self.opperation_list = opperation_list
        self.column = None
        self.data = None
        self.target_list = sql_list

    def write(self):
        self.target_list[self.target_pos][1] = self.data
        return


    def wav_split(self):
        try:
            start = float(self.data[:4].strip())
            stop = float(self.data[-4:].strip())
        except:
            raise RuntimeError(
                  "Failed to wav_split: {}".format(self.data))
        #copy stop to the SQL list, start will be taken care of by write()
        self.target_list[self.target_pos + 1][1] = stop
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

    def geo_features(self):
        if 'rounded' in self.data:
            self.target_list[-2][1] = 1
        return

class QueryGenerator:
    def __init__(self):
        self.sim_query = 'INSERT INTO simulations ('
        self.geo_query = 'INSERT INTO '
        self.wire = ['length', 'width', 'thickness','corner_radius',
                    'rounded_corner']
        self.square = ['length', 'width', 'thickness', 'hole']
        self.geometries = {'wire' : self.wire,
                           'square' : self.square,
                           }
        self.adress = []

    def make_query(self, sql_list):
        sim_count = 0
        geo_count = 0
        #simulations query
        for col in sql_list[1:11]:
            if col[1] is not None:
                sim_count += 1
                self.sim_query += col[0]
                self.sim_query += ', '

        self.sim_query = self.sim_query[:-2]
        self.sim_query += ') VALUES ('
        self.sim_query += sim_count* '%s, '
        self.sim_query = self.sim_query[:-2]
        self.sim_query += ')'

        #geometry query
        for geo in self.geometries:
            if geo in sql_list[0][1]:
                self.geo_query += geo
                self.geo_query += ' ('
                current_geo = self.geometries[geo]
                break
        else:
            raise RuntimeError('Found no valid geometry in {}'.format(sql_list[0][1]))

        #select the attributes of the current geometry
        active_cols = [col for col in sql_list[10:] if col[0] in current_geo]

        for col in active_cols:
            if col[1] is not None:
                geo_count += 1
                self.geo_query += col[0]
                self.geo_query += ', '

        self.geo_query = self.geo_query[:-2]
        self.geo_query += ') VALUES ('
        self.geo_query += geo_count* '%s, '
        self.geo_query = self.geo_query[:-2]
        self.geo_query += ')'
        print(self.sim_query)
        for d in sql_list[1:11]:
            print(d)
        print(self.geo_query)
        for d in sql_list[11:]:
            print(d)
        print('\n')
        self.sim_query = 'INSERT INTO simulations ('
        self.geo_query = 'INSERT INTO '

        #Bad structure here: Turn the adress list into a str
        sql_list[10][1] = str(sql_list[10][1])
        #Try to execute the queries
        try:
            my_cursor.execute(self.sim_query,
                     tuple([col[1] for col in sql_list if col[1] is not None]))
        except Exception as e:
            print('Bad simulation query')
            print(e)

        return

    def loop_sql_lists(self, sql_list, list_cols):
        if len(list_cols) == 0:
            print('adress: ', self.adress)
            self.make_query(sql_list)
            return
        else:
            print('loop called')
            tup = list_cols.pop()
            current_list = tup[0]
            current_index = tup[1]
            self.adress.append(None)

            for i in range(len(current_list)):
                sql_list[current_index][1] = current_list[i]
                self.adress[-1] = i
                sql_list[10][1] = self.adress
                self.loop_sql_lists(sql_list, list_cols)

            #reset the adress
            sql_list[10][1] = None
            return



    def generate(self, sql_list):
        """
        This method gets a possibly nested sql_list.
        It splits them up and calls make_query for every simple list.
        """
        #find the colums which have list-values
        list_cols = [(col[1], sql_list.index(col)) for col in sql_list if type(col[1]) is list]
        list_cols.sort(key = lambda tup : len(tup[0]), reverse = True)
        print('list_cols: ', list_cols)
        #reset the adress
        self.adress = []
        self.loop_sql_lists(sql_list, list_cols)
        return



#Define the excel_list with one Exl for every column
exl_list = [Exl('m-file', 1, ),
            Exl('material', 2),
            Exl('cladding', 3),
            Exl('substrate', 4),
            Exl('geom', 0, [Exl.geo_features]),
            Exl('periode', 5),
            Exl('wavelength', 6, [Exl.wav_split]),
            Exl('points', 8),
            Exl('order', 9),
            Exl('length', 11, [Exl.evaluate, Exl.listify]),
            Exl('width', 12, [Exl.evaluate, Exl.listify]),
            Exl('thickness', 13, [Exl.evaluate, Exl.listify]),
            Exl('corner radius', 14),
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


####Main loop: Generate SQL-queries for every Excel row
query_gen = QueryGenerator()
for row in ws.iter_rows(name_row[0].row + 1, 8):
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

    query_gen.generate(sql_list)




    """
    for col in sql_list:
        print(col)
    for exl in exl_list:
        print(exl.name, '  ,  ',exl.data)
    """
    #Use the exl_list to populate the sql_list
