import subprocess
import sqlite3
from scipy.io import loadmat
import re
import numpy as np
import os
import random
import shelve


class Crawler:
    """This Modul allows to load S-matrices from a target directory. Find the
    nessecary name/ID in the 'meta_materials.db'. You need to be able to execute
    Bash commands. For example usage look below in the 'if name == main' section.

    Parameters
    ----------
    directory : str
                path to directory containing the .mat/.npy files
    cursor : sqlite3 cursor to 'meta_materials.db'
    """
    def __init__(self, directory, cursor = None):
        self.directory = directory
        self.cursor = cursor
        self.files = os.listdir(self.directory)

    def find_path(self, name):
        bashCommand = 'find {} -name *{}_Daten_gesamt.mat -print -quit'.format(self.directory, name)
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
            adress = eval(adress,{"__builtins__":None})
        return self.find_smat(name, adress)

    def load_smat_npy(self, name, adress=None):
        if type(adress) is str:
            adress = eval(adress,{"__builtins__":None})

        smat = np.load("{}/{}{}.npy".format(self.directory, name, adress))
        return smat


    def load_smat_by_id_npy(self, id):
        query = 'SELECT m_file, adress FROM simulations WHERE simulation_id = {}'.format(id)
        self.cursor.execute(query)
        row = self.cursor.fetchone()

        smat = self.load_smat_npy(name=row[0], adress=row[1])
        return smat

    def load_random_smat_npy(self):
        """
        Loads a random smat from a directory of .npy files
        self.directory has to point to a .npy directory

        Returns
        -------
        smat : LX4X4 Array

        """
        file = random.choice(self.files)
        smat = np.load("{}/{}".format(self.directory, file))
        return smat

    def extract_all(self, target_dir):
        """
        CAREFULL: This copies files to the target_dict.
        For every destict m_file name in meta_materials.db this methode looks
        for 'm_file*Daten_gesamt.mat' in self.directory and copies it to target_dir.
        """
        self.cursor.execute('select m_file from simulations')
        names = [name[0] for name in self.cursor.fetchall()]
        names = set(names)
        for m_file in names:
            path = self.find_path(m_file)
            bashCommand = 'cp {} {}'.format(path, target_dict)
            print(bashCommand)
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()


    def extract_params(self, id):
        """Queries meta_materials.db for all the data to the given ID.

        Parameters
        ----------
        id : int

        Returns
        -------
        param_dict : dict
                     Contains the combined data from the simulations and
                     geometry tables with coresponding names
        """
        #query for the simulation_data of id
        query = 'SELECT * FROM simulations WHERE simulation_id = {}'.format(id)
        self.cursor.execute(query)
        simulation_data = list(self.cursor.fetchall()[0])


        #query for the names to simulation_data
        query = """SELECT sql FROM sqlite_master
                   WHERE tbl_name = 'simulations' AND type = 'table'"""
        self.cursor.execute(query)
        simulation_names = self.cursor.fetchone()[0]

        #parse out the names using RegEx
        pattern = re.compile(r'\n\s+([a-z_]+)')
        matches = pattern.finditer(simulation_names)
        simulation_names = [match.group(1) for match in matches]

        #join names and data into a dict
        simulation_dict = dict(zip(simulation_names, simulation_data))

        #repeat the process for the geometry-table
        geo = simulation_dict['geometry']
        query = 'SELECT * FROM {} WHERE simulation_id = {}'.format(geo, id)
        self.cursor.execute(query)
        geo_data = self.cursor.fetchall()[0]

        query = "SELECT sql FROM sqlite_master WHERE tbl_name = '{}' AND type = 'table'".format(geo)
        self.cursor.execute(query)
        geo_names = self.cursor.fetchone()[0]

        pattern = re.compile(r'\n\s+([a-z_]+)')
        matches = pattern.finditer(geo_names)
        geo_names = [match.group(1) for match in matches]
        geo_dict = dict(zip(geo_names, geo_data))
        del geo_dict['simulation_id']

        #join the two dicts
        param_dict = {**simulation_dict, **geo_dict}

        return param_dict

    def check_db_for_correct_dimensions(self):
        working = 0
        all = 0
        self.cursor.execute('SELECT simulation_id FROM simulations WHERE angle_of_incidence=0 AND geometry="square"')
        ids = [id[0] for id in self.cursor.fetchall()]
        for id in ids:
            all += 1
            print('checking ID: ', id)

            try:
                #load smat and parameters
                smat = self.find_smat_by_id(id)
                param_dict = self.extract_params(id)
                #extract relevant parameters
                L = param_dict['spectral_points']
                assert smat.shape == (L, 4, 4)

            except Exception as e:
                print('couldnt load smat:')
                print(e)
                continue
            working += 1
        print('{} out of {} entries working'.format(working, all))

    def convert_to_npy(self, ids):
        """
        Loads the .mat files for all the IDs, splits them into one file per ID
        and saves them as .npy files for quicker access
        Also extracts the parameters of every ID and saves them to a shelve file

        Parameters
        ----------
        ids : list
        """
        with shelve.open("smat_params.shelve") as d:
            for id in ids:
                print("converting id: ", id)
                #save smat
                query = 'SELECT m_file, adress FROM simulations WHERE simulation_id = {}'.format(id)
                self.cursor.execute(query)
                row = self.cursor.fetchone()
                name = row[0]
                adress = row[1]
                if type(adress) is str:
                    adress = eval(adress,{"__builtins__":None})

                fullname = "{}{}.npy".format(name, adress)
                smat = self.find_smat(name, adress)
                np.save("smat_data/{}".format(fullname), smat)
                #save params
                params = self.extract_params(id)
                d[fullname] = params

            d.close()


def mat_print(mat):
    for i in range(4):
        print('{:+.2f} {:+.2f} {:+.2f} {:+.2f}'.format(mat[i, 0], mat[i,1], mat[i,2], mat[i,3]))


#%%
if __name__ == '__main__':
    #create a crawler object
    conn = sqlite3.connect('meta_materials.db')
    cursor = conn.cursor()
    crawler = Crawler(directory='../collected_mats', cursor=cursor)

    cursor.execute("""SELECT simulation_id FROM simulations
                   WHERE angle_of_incidence=0
                   AND geometry = 'square'
                   AND wavelength_start = 0.5
                   AND wavelength_stop = 1
                   AND spectral_points =  128""")
    ids = [id[0] for id in cursor.fetchall()]

    crawler.convert_to_npy(ids)
