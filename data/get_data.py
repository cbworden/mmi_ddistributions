#!/usr/bin/env python

import os

import numpy as np
import pandas as pd
import scipy.constants as sp
from shakelib.gmice.wgrw12 import WGRW12
# from shakelib.multigmpe import MultiGMPE
from openquake.hazardlib.imt import PGA, PGV, SA

# Since this is currently just CA earthquakes, lets just use the NSHMP ACR
# GMPEs (active_crustal_nshmp2014)
# from openquake.hazardlib.gsim.abrahamson_2014 import AbrahamsonEtAl2014
# from openquake.hazardlib.gsim.boore_2014 import BooreEtAl2014
# from openquake.hazardlib.gsim.campbell_bozorgnia_2014 import CampbellBozorgnia2014
# from openquake.hazardlib.gsim.chiou_youngs_2014 import ChiouYoungs2014

MSS_TO_G = 1 / sp.g
M_TO_CM = 1 / 100
CSS_TO_G = MSS_TO_G * M_TO_CM


COL_NAMES = [
    'event_id',
    'sta_lat',
    'sta_lon',
    'mmi',
    'pga',
    'pgv',
    'psa03',
    'psa10',
    'psa30',
    'r_hypo',
    'hypo_lat',
    'hypo_lon',
    'magnitude',
    'hypo_depth',
    'n_dyfi',
    'vs30',
    'inst_to_mmi_dist',
    'std_mmi_boot',
    'mean_mmi_boot',
    'std_pga_at_dyfi',  # EMT: I don't think I know what this is.
    'std_pgv_at_dyfi',
    'std_psa03_at_dyfi',
    'std_psa10_at_dyfi',
    'std_psa30_at_dyfi'
]

IMTS = [
    ('pgv', PGV()),
    ('pga', PGA()),
    ('psa03', SA(0.3)),
    ('psa10', SA(1.0)),
    ('psa30', SA(3.0))
]


def read_shake_data():
    """
    Since shakeGrid.csv doesn't have column names, this is a
    convenience function for loading it into a data frame
    and correctly handling the row names.
    """
    this_mod = os.path.dirname(os.path.abspath(__file__))

    data_file = os.path.join(this_mod, 'shakeGrid.csv')
    shake_df = pd.read_csv(data_file, header=None, names=COL_NAMES)

    # There are some records where IMTs are zero. This causes -Inf values when
    # PGV is logged so lets remove, recognizing that this will probably result
    # in unpredictable pandas behvior.
    idx_keep = np.where(
        (shake_df['pga'] > 0) &
        (shake_df['pgv'] > 0) &
        (shake_df['psa03'] > 0) &
        (shake_df['psa10'] > 0) &
        (shake_df['psa30'] > 0)
    )[0]
    shake_df = shake_df.iloc[idx_keep]

    # Perhaps this will prevent unpredictable indexing.
    shake_df = shake_df.reset_index()

    # Oh, but of course that has created a new column called "index", what a
    # a bunch of ass hats...
    shake_df = shake_df.drop(columns=['index'])

    # Append predictions and residuals
    gmice = WGRW12()

    for imt, IMT in IMTS:
        imt_data = np.array(shake_df[imt])
        if imt != 'pgv':
            # Convert from cm/s/s to g?
            imt_data = imt_data * CSS_TO_G
        log_imt = np.log(imt_data)
        mmi_pred, dmda = gmice.getMIfromGM(
            log_imt, IMT, dists=shake_df['r_hypo'],
            mag=shake_df['magnitude'])
        mmi_residuals = np.array(shake_df['mmi']) - mmi_pred
        shake_df['mmi_from_%s' % imt] = mmi_pred
        shake_df['mmi_res_%s' % imt] = mmi_residuals

    # Append updated CA Vs30 values
    vs30_file = 'shakeGrid_add_vs30.csv'
    vs30_df = pd.read_csv(vs30_file)
    shake_df['CA Vs30'] = vs30_df['CA Vs30']

    # Append distances

    # Append GMPE means and standard deviations

    return shake_df
