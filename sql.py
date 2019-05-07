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
          ['length', None],
          ['width', None],
          ['thickness', None],
          ['corner_radius', 'Null'],
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

    def make_query(self, sql_list):
        #simulations query
        for col in sql_list[1:10]:
            self.sim_query += col[0]
            self.sim_query += ', '

        self.sim_query = self.sim_query[:-2]
        self.sim_query += ') VALUES ('
        self.sim_query += 9* '%s, '
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
            self.geo_query += col[0]
            self.geo_query += ', '

        self.geo_query = self.geo_query[:-2]
        self.geo_query += ') VALUES ('
        self.geo_query += len(active_cols)* '%s, '
        self.geo_query = self.geo_query[:-2]
        self.geo_query += ')'
        return

    def generate(self, sql_list):
        """
        This method gets a possibly nested sql_list.
        It splits them up and calls make_query for every simple list.
        """
        


#Define the excel_list with one Exl for every column
exl_list = [Exl('m-file', 1, ),
            Exl('material', 2),
            Exl('cladding', 3),
            Exl('substrate', 4),
            Exl('geom', 0),
            Exl('periode', 5),
            Exl('wavelength', 6, [Exl.wav_split]),
            Exl('points', 8),
            Exl('order', 9),
            Exl('length', 10, [Exl.evaluate, Exl.listify]),
            Exl('width', 11, [Exl.evaluate, Exl.listify]),
            Exl('thickness', 12, [Exl.evaluate, Exl.listify]),
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
for row in ws.iter_rows(name_row[0].row + 1, 4):
    #Load the data of the row
    for i in range(len(row)):
        for exl in exl_list:
            if i == exl.column:
                exl.data = row[i].value

    for exl in exl_list:
        for opperation in exl.opperation_list:
            opperation(exl)
        exl.write()

    query_gen.make_query(sql_list)
    print(query_gen.sim_query)
    print(query_gen.geo_query)



    """
    for col in sql_list:
        print(col)
    for exl in exl_list:
        print(exl.name, '  ,  ',exl.data)
    """
    #Use the exl_list to populate the sql_list
