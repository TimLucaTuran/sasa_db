import subprocess
import sqlite3
from scipy.io import loadmat


class Crawler:
    """This Modul allows to load S-matrices from a target directory. Find the
    nessecary name/ID in the 'meta_materials.db'. You need to be able to execute
    Bash commands. For example usage look below in the 'if name == main' section.

    Parameters
    ---------------
    directory : path to directory containing the .mat files
    cursor : sqlite3 cursor to 'meta_materials.db'
    """
    def __init__(self, directory, cursor = None):
        self.directory = directory
        self.cursor = cursor

    def find_path(self, name):
        bashCommand = 'find {} -name *{}*.mat -print -quit'.format(self.directory, name)
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        path = output[:-1].decode('UTF-8')
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
                raise ValueError(
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
        return self.find_smat(name, adress)



    def extract_all(self, target_dict):
        """CAREFUL: This method copies all the useful .mat files from self.directory
        to target_dict."""

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
        #currently just for the square geometry
        query = '''SELECT particle_material, cladding, substrate, periode, wavelength_start,
        wavelength_stop FROM simulations WHERE simulation_id = {}'''.format(id)
        self.cursor.execute(query)
        simulation = self.cursor.fetchone()
        query2 = 'SELECT width, thickness FROM square WHERE simulation_id = {}'.format(id)
        self.cursor.execute(query2)
        geometry = self.cursor.fetchone()
        keys = ['particle_material', 'cladding', 'substrate','periode',
                'wavelength_start', 'wavelength_stop', 'width', 'thickness']
        vals = simulation + geometry
        dict = {keys[i] : vals[i] for i in range(len(vals))}
        return dict

    def check_db_for_correct_dimensions(self):
        working = 0
        all = 0
        self.cursor.execute('SELECT simulation_id FROM simulations')
        ids = [id[0] for id in self.cursor.fetchall()]
        for id in ids:
            all += 1
            print('checking ID: ', id)
            try:
                smat = self.find_smat_by_id(id)
            except Exception as e:
                print('couldnt load smat:')
                print(e)
                continue
            '''
            self.cursor.execute("""SELECT adress, m_file FROM simulations WHERE
            simulation_id == {}""".format(id))
            row = self.cursor.fetchone()
            adress = eval(row[0])
            if len(smat.shape) != len(adress):
                print('ID: ', id,'Name: ', row[1])
                print('has unexpected shape: ', smat.shape)
                continue
            '''
            print('Entry clean')
            working += 1
        print('{} out of {} entries working'.format(working, all))


def mat_print(mat):
    for i in range(4):
        print('{:+.2f} {:+.2f} {:+.2f} {:+.2f}'.format(mat[i, 0], mat[i,1], mat[i,2], mat[i,3]))


#%%
if __name__ == '__main__':
    #create a crawler object
    conn = sqlite3.connect('meta_materials.db')
    cursor = conn.cursor()
    crawler = Crawler(directory='collected_mats/', cursor=cursor)

    #load and print a S-Mat
    mat = crawler.find_smat('HyperVis_al_square_holes_1')
    mat.shape
    #load the paramesters of the S-Mat

    """dict = crawler.extract_params(id = 282)
    crawler.check_db_for_correct_dimensions()
"""
