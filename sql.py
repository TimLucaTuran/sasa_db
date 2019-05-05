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
          ['corner_radius', None],
          ['radius', None],
          ['rounded_corner', None],
          ['hole', None],
          ]

          #Define the Excel-Struct it holds information of a Excel-Cell and which
          #opperations need to be applied. For example the wavelength excel cell:
          #"0.64 ... 1.7" needs to be split into wavelength_start and _stop
          class ExcelStruct:
              def __init__(self, name, target_pos, opperation_list):
                  self.name = name
                  self.target_pos = target_pos
                  self.opperation_list = opperation_list
                  self.column = None
                  self.data = None
                  self.target_list = sql_list

                  #opperations
                  def wav_split(self):
                      try:
                          start = float(self.data[:4].strip())
                          start = float(self.data[-4:].strip())
                      except:
                          raise RuntimeError(
                          "Failed to wav_split: {}".format(self.data))
                      


#Define the excel_list with one ExcelStruct for every column
exl_list = [ExcelStruct('m-file', 1, ),
            ExcelStruct('material', 2),
            ExcelStruct('cladding', 3),
            ExcelStruct('substrate', 4),
            ExcelStruct('geom', 0),
            ExcelStruct('periode', 5),
            ExcelStruct('wavelength', 6),
            ExcelStruct('points', 8),
            ExcelStruct('order', 9),
            ExcelStruct('length', 10),
            ExcelStruct('width', 11),
            ExcelStruct('thickness', 12),
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
for row in ws.iter_rows(name_row[0].row + 1, ws.max_row):
    #Load the data of the row
    for i in range(len(row)):
        for exl in exl_list:
            if i == exl.column:
                exl.data = row[i].value
    """
    for exl in exl_list:
        print(exl.name, '  ,  ',exl.data)
    """
    #Use the exl_list to populate the sql_list



    break
