#!/usr/bin/env python

import sys
import os

import pandas as pd
import numpy as np

from openquake.hazardlib.gsim import base
import openquake.hazardlib.imt as imt
from openquake.hazardlib.const import StdDev

# Pick an IPE
from openquake.hazardlib.gsim.allen_2012_ipe import AllenEtAl2012

from gmpe import ngaw2

sys.path.append(os.path.join('..', 'data'))
import get_data

# Read in the data
SHAKE_DF = get_data.read_shake_data()


def main():
    gmpe = ngaw2()
    ipe = AllenEtAl2012()

    event_ids = np.unique(SHAKE_DF['event_id'])

    i = 0

    event_id = event_ids[i]
    idx = np.where(SHAKE_DF['event_id'] == event_id)[0]

    rx = base.RuptureContext()
    rx.mag = np.array(SHAKE_DF['magnitude'])[idx]
    rx.ztor = np.array(SHAKE_DF['ztor'])[idx]
    rx.rake = np.full_like(rx.mag)
    rx.width =
    rx.hypo_depth = np.array(SHAKE_DF['hypo_depth'])[idx]

    sx = base.SitesContext()
    sx.vs30 = np.array(SHAKE_DF['CA Vs30'])[idx]

    dx = base.DistancesContext()
    dx.rjb = np.array(SHAKE_DF['r_jb'])[idx]
    dx.rrup = np.array(SHAKE_DF['r_rup'])[idx]
    dx.rx = np.array(SHAKE_DF['r_x'])[idx]
    dx.ry = np.array(SHAKE_DF['r_y'])[idx]
    dx.ry0 = np.array(SHAKE_DF['r_y0'])[idx]

    lmean, lsd = gmpe.get_mean_and_stddevs(
        sx, rx, dx, imt=IMTS[j], stddev_types=STD)


if __name__ == '__main__':
    main()
