import subprocess
from scipy.io import loadmat
import mysql.connector as mc

class Crawler:
    def __init__(self, directory):
        self.directory = directory

    def find_path(self, name):
        bashCommand = 'find {} -name *{}*.mat -print'.format(self.directory, name)

        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        path = output[:-1].decode('UTF-8')
        return path

    def find(self, name):
        path = self .find_path(name)
        smat = loadmat(path)
        print(smat['SMAT_'].shape)
        return smat

    def extract_all(self, target_dict):
        mydb = mc.connect(
            host = "localhost",
            user = "root",
            passwd = "tltit69z",
            database = "meta_materials",
        )
        cursor = mydb.cursor()
        cursor.execute('select m_file from simulations')
        names = [name[0] for name in cursor.fetchall()]
        names = set(names)
        for m_file in names:
            path = self.find_path(m_file)
            bashCommand = 'cp {} {}'.format(path, target_dict)
            print(bashCommand)
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print(output, error)

crawler = Crawler(directory='/run/media/tim/D4C5-A3BA/')
#%%

crawler.find('Chi_RotWire_1_rounded_Ti_n')
crawler.extract_all(target_dict='/home/tim/Desktop/smat_test')
