import subprocess
from scipy.io import loadmat
import mysql.connector as mc

def mat_print(mat):
    for i in range(4):
        print('{:+.2f} {:+.2f} {:+.2f} {:+.2f}'.format(mat[i, 0], mat[i,1], mat[i,2], mat[i,3]))

class Crawler:
    def __init__(self, directory, cursor = None):
        self.directory = directory
        self.cursor = cursor

    def find_path(self, name):
        print(name)
        bashCommand = 'find {} -name *{}*.mat -print -quit'.format(self.directory, name)

        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        path = output[:-1].decode('UTF-8')
        print(path)
        return path


    def find_smat(self, name, adress=None):
        path = self.find_path(name)
        smat = loadmat(path)['SMAT_']
        if adress is None:
            return smat
        else:
            wav_length_dim = smat.shape[-3]
            adress += [slice(wav_length_dim), slice(4), slice(4)]
            if len(smat.shape) != len(adress):
                raise RuntimeError(
                'ERROR: S-Mat {} has unexpected shape: {}'.format(name, smat.shape))
            return smat[tuple(adress)]

    def find_smat_by_id(self, id):
        query = 'SELECT m_file, adress FROM simulations WHERE simulation_id = {}'.format(id)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        name = row[0]
        adress = row[1]
        if type(adress) is str:
            adress = eval(adress)
        print('ID: ',id,' has adress: ', adress)
        return self.find_smat(name, adress)



    def extract_all(self, target_dict):
        self.cursor.execute('select m_file from simulations')
        names = [name[0] for name in self.cursor.fetchall()]
        names = set(names)
        for m_file in names:
            path = self.find_path(m_file)
            bashCommand = 'cp {} {}'.format(path, target_dict)
            print(bashCommand)
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print(output, error)


    def extract_params(self, id):
        query = '''SELECT  particle_material, cladding, substrate, periode, wavelength_start,
        wavelength_stop FROM simulations WHERE simulation_id = {}'''.format(id)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        query2 = 'SELECT length, width, thickness FROM wire WHERE simulation_id = {}'.format(id)
        self.cursor.execute(query2)
        geo = self.cursor.fetchone()
        return list(row + geo)

    def find_ids(self):
        query = 'SELECT simulation_id FROM simulations WHERE m_file LIKE "Chi_RotWire%"'
        self.cursor.execute(query)
        ids = [id[0] for id in self.cursor.fetchall()]
        return ids


#%%
if __name__ == '__main__':
    mydb = mc.connect(
        host = "localhost",
        user = "root",
        passwd = "tltit69z",
        database = "meta_materials",
    )
    cursor = mydb.cursor(buffered=True)

#%%
    crawler = Crawler(directory='/run/media/tim/D4C5-A3BA/', cursor=cursor)
    ids = crawler.find_ids()
    smat = crawler.find_smat_by_id(ids[0])
    mat_print(smat[0,:,:])
    #mat = crawler.find_smat('Chi_RotWire_1_rounded_Ti_n', adress=[1,1,1])
    #mat_print(mat[0,:,:])
    #crawler.extract_params('Chi_RotWire_1_rounded_Ti_n')
    #crawler.extract_all(target_dict='/home/tim/Desktop/S_matrices')
    crawler2 = Crawler(directory='/home/tim/Desktop/S_matrices', cursor=cursor)
    mat = crawler2.find_smat('Chi_RotWire_1_rounded_Ti_n', adress=[1,1,1])
    mat_print(mat[0,:,:])
