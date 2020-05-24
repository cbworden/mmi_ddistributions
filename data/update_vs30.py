#!/usr/bin/env python


import sys
import os

import matplotlib.pyplot as plt
import numpy as np

from mapio.gdal import GDALGrid

sys.path.append(os.path.join('..', 'data'))
import get_data

# Read in the data
SHAKE_DF = get_data.read_shake_data()

VS30_FILE = '/Users/emthompson/data/Thompson2014/Wills15_hybk_3c_2020.tif'


def main():
    """
    Read in data and add comcat IDs, download rupture file if available.
    """
    Vs30grid = GDALGrid.load(VS30_FILE)
    slats = np.array(SHAKE_DF['sta_lat'])
    slons = np.array(SHAKE_DF['sta_lon'])

    new_vs30 = Vs30grid.getValue(slats, slons, method='nearest')

    fig, ax = plt.subplots(1)
    ax.loglog(SHAKE_DF['vs30'], new_vs30, 'ko', fillstyle='none')
    # ax.set(xscale="log", yscale="log")
    lim = [100, 2000]
    ax.plot(lim, lim, 'k--')
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel('Old Vs30')
    ax.set_ylabel('New Vs30')
    fig_path = os.path.join('..', 'figs', 'vs30_compare.png')
    fig.savefig(fig_path, dpi=300)

    n_nan = len(np.where(np.isnan(new_vs30))[0])
    print('There are %s nans.' % n_nan)

    SHAKE_DF['CA Vs30'] = new_vs30
    new_file = 'shakeGrid_add_vs30.csv'
    SHAKE_DF.to_csv(new_file, index=False)


if __name__ == '__main__':
    main()
