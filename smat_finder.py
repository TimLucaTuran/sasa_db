import subprocess
from scipy.io import loadmat

class Crawler:
    def __init__(self, directory):
        self.directory = directory

    def find(self, name):
        bashCommand = 'find {} -name *{}*.mat -print'.format(self.directory, name)
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        path = output[:-1].decode('UTF-8')
        smat = loadmat(path)
        print(smat['SMAT_'].shape)


crawler = Crawler(directory='/run/media/tim/D4C5-A3BA/')
crawler.find('Chi_RotWire_1_rounded_Ti_n')
