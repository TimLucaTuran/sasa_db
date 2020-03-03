import os

os.system("rm meta_materials.db")
os.system("python db_setup.py")

exl_sheets = [10, 11, 13, 14, 16, 22]
for sheet in exl_sheets:
    print("working on sheet ", sheet)
    os.system("python exl_to_sql.py -db meta_materials.db -exl project_overview.xlsx -n {}".format(sheet))
