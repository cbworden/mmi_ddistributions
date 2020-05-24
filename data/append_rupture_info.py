#!/usr/bin/env python

import sys
import os

import pandas as pd
import numpy as np

from shakelib.rupture.factory import get_rupture
from shakelib.rupture.origin import Origin

sys.path.append(os.path.join('..', 'data'))
import get_data

# Read in the data
SHAKE_DF = get_data.read_shake_data()


# file with event info and comcat IDs where available
EVENT_FILE = 'events_comcat.csv'

# historic event file
HIST_FILE = 'historic_events.txt'
HIST_COLS = [
    'id',
    'magnitude',
    'date',
    'time',
    'lat',
    'lon',
    'dep',
    'comcat_id'
]


def main():
    new_df = append_rup_info(SHAKE_DF)
    new_file = 'shakeGrid_add_rup_info.csv'
    new_df.to_csv(new_file, index=False)


def append_rup_info(shake_df):
    # Add columns for things we will populate
    shake_df['ztor'] = np.nan
    shake_df['dip'] = np.nan
    shake_df['r_rup'] = np.nan
    shake_df['r_rup_var'] = np.nan
    shake_df['r_jb'] = np.nan
    shake_df['r_jb_var'] = np.nan
    shake_df['r_x'] = np.nan
    shake_df['r_y'] = np.nan
    shake_df['r_y0'] = np.nan

    eq_df = pd.read_csv(EVENT_FILE)
    hist_eq_df = pd.read_csv(
        HIST_FILE, sep=' ', header=None, names=HIST_COLS)

    # Event dictionary template
    edict = {
        'mag': np.nan,
        'id': 'dummy',
        'locstring': 'dummy',
        'mech': 'ALL',
        'lon': np.nan,
        'lat': np.nan,
        'depth': np.nan,
        'netid': "",
        'network': "",
        'time': ""
    }

    # -------------------------------------------------------------------------
    # First do historic events
    print('Historic events...')
    n_hist = hist_eq_df.shape[0]
    for i in range(n_hist):
        print('    i = %s of %s' % (i, n_hist))
        ref_id = hist_eq_df['id'][i]
        com_id = hist_eq_df['comcat_id'][i]

        # Make an origin
        edict['mag'] = hist_eq_df['magnitude'][i]
        edict['lon'] = hist_eq_df['lon'][i]
        edict['lat'] = hist_eq_df['lat'][i]
        edict['depth'] = hist_eq_df['dep'][i]
        origin = Origin(edict)

        # Is there a comcat id?
        if isinstance(com_id, str):
            # Is there a rupture?
            rup_dir = os.path.abspath(os.path.join('ruptures', com_id))
            if os.path.exists(rup_dir):
                rup_file = os.path.join(rup_dir, 'rupture.json')
                rup = get_rupture(origin, rup_file)
            else:
                # No rupture file, so make a point rupture:
                rup = get_rupture(origin)

            # Things that don't need sites
            ztor = rup.getDepthToTop()
            dip = rup.getDip()

            # Get site lat/lons for this eqk
            idx = np.where(shake_df['event_id'] == ref_id)[0]
            if len(idx):
                sta_lat = np.array(shake_df['sta_lat'][idx])
                sta_lon = np.array(shake_df['sta_lon'][idx])
                rjb, rjb_var = rup.computeRjb(
                    sta_lon, sta_lat, np.zeros_like(sta_lat))
                rrup, rrup_var = rup.computeRrup(
                    sta_lon, sta_lat, np.zeros_like(sta_lat))
                gc2_dict = rup.computeGC2(
                    sta_lon, sta_lat, np.zeros_like(sta_lat))

                shake_df.at[idx, 'ztor'] = ztor
                shake_df.at[idx, 'dip'] = dip
                shake_df.at[idx, 'r_rup'] = rrup
                shake_df.at[idx, 'r_rup_var'] = rrup_var
                shake_df.at[idx, 'r_jb'] = rjb
                shake_df.at[idx, 'r_jb_var'] = rjb_var
                shake_df.at[idx, 'r_x'] = gc2_dict['rx']
                shake_df.at[idx, 'r_y'] = gc2_dict['ry']
                shake_df.at[idx, 'r_y0'] = gc2_dict['ry0']

    # -------------------------------------------------------------------------
    # Now do the rest
    print('Non-historic events...')
    n_events = eq_df.shape[0]
    for i in range(n_events):
        print('    i = %s of %s' % (i, n_events))
        ref_id = eq_df['id'][i]
        com_id = eq_df['comcat_id'][i]

        # Make an origin
        edict['mag'] = eq_df['mag'][i]
        edict['lon'] = eq_df['lon'][i]
        edict['lat'] = eq_df['lat'][i]
        edict['depth'] = eq_df['dep'][i]
        origin = Origin(edict)

        # Is there a comcat id?
        if isinstance(com_id, str):
            # Is there a rupture?
            rup_dir = os.path.abspath(os.path.join('ruptures', com_id))
            if os.path.exists(rup_dir):
                rup_file = os.path.join(rup_dir, 'rupture.json')
                rup = get_rupture(origin, rup_file)
            else:
                # No rupture file, so make a point rupture:
                rup = get_rupture(origin)

            # Things that don't need sites
            ztor = rup.getDepthToTop()
            dip = rup.getDip()

            # Get site lat/lons for this eqk
            idx = np.where(shake_df['event_id'] == ref_id)[0]
            if len(idx):
                sta_lat = np.array(shake_df['sta_lat'][idx])
                sta_lon = np.array(shake_df['sta_lon'][idx])
                rjb, rjb_var = rup.computeRjb(
                    sta_lon, sta_lat, np.zeros_like(sta_lat))
                rrup, rrup_var = rup.computeRrup(
                    sta_lon, sta_lat, np.zeros_like(sta_lat))
                gc2_dict = rup.computeGC2(
                    sta_lon, sta_lat, np.zeros_like(sta_lat))

                shake_df.at[idx, 'ztor'] = ztor
                shake_df.at[idx, 'dip'] = dip
                shake_df.at[idx, 'r_rup'] = rrup
                shake_df.at[idx, 'r_rup_var'] = rrup_var
                shake_df.at[idx, 'r_jb'] = rjb
                shake_df.at[idx, 'r_jb_var'] = rjb_var
                shake_df.at[idx, 'r_x'] = gc2_dict['rx']
                shake_df.at[idx, 'r_y'] = gc2_dict['ry']
                shake_df.at[idx, 'r_y0'] = gc2_dict['ry0']

    return shake_df


if __name__ == '__main__':
    main()
