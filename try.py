import crawler
import numpy as np
import sqlite3
import os
from scipy.stats import unitary_group
"""
# calculates the operator norm of a given matrix
def op_norm(mat):

    return norm
"""
def star_product_analyt(SIN_1,SIN_2):
    """
    Calculate Lifeng Li's starproduct for two S-matrices SIN_1 and SIN_2,
    such that S = S1 * S2. The starproduct between two arbitrary S-matrices
    was precalculated analytically with Mathematica.

    Parameters
    ----------
    SIN_1, SIN_2 : HxLx4x4 numpy array
                   H is height_vec_len, the dimension of the height vector
                   given to the layer object. (Most of the time equal to 1)
                   L is wav_vec_len the number of measured wavelengths

    Returns
    -------
    s_out : HxLx4x4 numpy array
    """
    # height_vec_len = max(SIN_1.shape[0], SIN_2.shape[0])
    # S-matrix 1
    TF_1 = SIN_1[:,0:2,0:2]
    TB_1 = SIN_1[:,2:4,2:4]
    RF_1 = SIN_1[:,2:4,0:2]
    RB_1 = SIN_1[:,0:2,2:4]
    # S-matrix 2
    TF_2 = SIN_2[:,0:2,0:2]
    TB_2 = SIN_2[:,2:4,2:4]
    RF_2 = SIN_2[:,2:4,0:2]
    RB_2 = SIN_2[:,0:2,2:4]
    # number of wavelengths
    wav_vec_len = SIN_1.shape[0]
    # declare output matrix
    s_out = np.zeros((wav_vec_len,4,4)).astype(complex)

    left_kernel = np.linalg.inv(np.eye(2) - RB_1 @ RF_2)
    right_kernel = np.linalg.inv(np.eye(2) - RF_2 @ RB_1)

    TF = TF_2 @ left_kernel @ TF_1
    TB = TB_1 @ right_kernel @ TB_2
    RF = RF_1 + TB_1 @ RF_2 @ left_kernel @ TF_1
    RB = RB_2 + TF_2 @ RB_1 @ right_kernel @ TB_2
    # Assemble the resulting s-matrix using the elements from above
    s_out[:,0:2,0:2] = TF
    s_out[:,2:4,2:4] = TB
    s_out[:,2:4,0:2] = RF
    s_out[:,0:2,2:4] = RB
    return s_out

def uni_check(mat):
    diff= np.linalg.inv(mat)-np.conjugate(mat).transpose()
    return diff

conn = sqlite3.connect("meta_materials.db")
cursor = conn.cursor()

crawler_new = crawler.Crawler(directory="collected_mats", cursor=cursor)
# ids = crawler.find_ids()

print("1. matrix: ")
# current = crawler_new.find_smat_by_id(61)
current = np.zeros((64,4,4)).astype(complex)
for i in range(64):
    # current[i,:,:] = np.matrix([[1,0,1j,0],[1j,0,1,0],[0,1,0,0],[0,0,0,1]])
    current[i,:,:] = unitary_group.rvs(4)
crawler.mat_print(current[0])

print("2. matrix: ")
current_2 = crawler_new.find_smat_by_id(61)
crawler.mat_print(current_2[0])
print("Star Product:")
crawler.mat_print(star_product_analyt(star_product_analyt(current_2,current_2),current_2)[0])
"""
"""
#cursor.execute("""select * from simulations;""")
#print(cursor.fetchone())
