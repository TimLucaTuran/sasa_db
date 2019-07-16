import subprocess
from scipy.io import loadmat
import mysql.connector as mc

def mat_print(mat):
    for i in range(4):
        print('{:+.2f} {:+.2f} {:+.2f} {:+.2f}'.format(mat[i, 0], mat[i,1], mat[i,2], mat[i,3]))

class Crawler:
    def __init__(self, directory):
        self.directory = directory
        self.target_dict = None
        self.cursor = None

    def find_path(self, name):
        bashCommand = 'find {} -name *{}*.mat -print'.format(self.directory, name)

        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        path = output[:-1].decode('UTF-8')
        return path


    def find(self, name, adress=None):
        path = self.find_path(name)
        smat = loadmat(path)['SMAT_']
        if adress is None:
            return smat
        else:
            wav_length_dim = smat.shape[-3]
            adress += [slice(wav_length_dim), slice(4), slice(4)]
            return smat[tuple(adress)]

    def extract_all(self):
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


    def extract_params(self,name):
        mydb = mc.connect(
            host = "localhost",
            user = "root",
            passwd = "tltit69z",
            database = "meta_materials",
        )
        cursor = mydb.cursor(buffered=True)
        query = '''SELECT  simulation_id, particle_material, cladding, substrate, periode, wavelength_start,
        wavelength_stop FROM simulations WHERE m_file = "{}"'''.format(name)
        cursor.execute(query)
        row = cursor.fetchone()
        id = row[0]
        query2 = 'SELECT length, width, thickness FROM wire WHERE simulation_id = {}'.format(id)
        cursor.execute(query2)
        geo = cursor.fetchone()
        return row + geo

#%%
if __name__ == '__main__':

    crawler = Crawler(directory='/run/media/tim/D4C5-A3BA/')
    mat = crawler.find('Chi_RotWire_1_rounded_Ti_n', adress=[1,1,1])
    mat_print(mat[0,:,:])
    crawler.extract_params('Chi_RotWire_1_rounded_Ti_n')
    #crawler.extract_all(target_dict='/home/tim/Desktop/smat_test')
