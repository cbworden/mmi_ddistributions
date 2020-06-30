#!/usr/bin/env python


import sys
import os
import shutil
import datetime

import pandas as pd
import numpy as np

from libcomcat.search import search
from shakelib.rupture.factory import get_rupture
from shakelib.rupture.origin import Origin
from shakelib.rupture.point_rupture import PointRupture

sys.path.append(os.path.join('..', 'data'))
import get_data

# Read in the data
SHAKE_DF = get_data.read_shake_data()

EVENT_FILE = 'events.txt'
EVENT_COLS = [
    'id',
    'mag',
    'date',
    'time',
    'lat',
    'lon',
    'dep'
]

dummy = {
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
origin = Origin(dummy)


def main():
    """
    Read in data and add comcat IDs, download rupture file if available.
    """
    eq_df = pd.read_csv(EVENT_FILE, sep=" ", header=None, names=EVENT_COLS)
    eq_df['comcat_id'] = ''
    nrows = eq_df.shape[0]

    for i in range(nrows):
        print('i = %i' % i)

        eqmag = float(eq_df['mag'][i])
        dmag = 0.3
        min_mag = eqmag - dmag
        max_mag = eqmag + dmag

        edate = eq_df['date'][i]
        etime = eq_df['time'][i]
        edatetime = edate + ' ' + etime

        eqdatetime = datetime.datetime.strptime(edatetime, '%Y/%m/%d %H:%M:%S')
        start_time = eqdatetime - datetime.timedelta(1)  # -1 day
        end_time = eqdatetime + datetime.timedelta(1)  # +1 day

        dll = 0.1
        eq_lat = float(eq_df['lat'][i])
        min_latitude = eq_lat - dll
        max_latitude = eq_lat + dll

        eq_lon = float(eq_df['lon'][i])
        min_longitude = eq_lon - dll
        max_longitude = eq_lon + dll

        summary_list = search(
            starttime=start_time,
            endtime=end_time,
            minlatitude=min_latitude,
            maxlatitude=max_latitude,
            minlongitude=min_longitude,
            maxlongitude=max_longitude,
            minmagnitude=min_mag,
            maxmagnitude=max_mag
        )

        if len(summary_list):
            summary_event = summary_list[0]
            detail = summary_event.getDetailEvent()
            eq_df.at[i, 'comcat_id'] = detail.id

            if (eqmag >= 5.5) & (detail.hasProduct('shakemap')):
                outdir = os.path.join('..', 'data', 'ruptures', detail.id)
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                shake = detail.getProducts('shakemap', source='preferred')[0]
                outfile = os.path.join(outdir, 'rupture.json')
                shake.getContent('rupture.json', outfile)

                # If it is a point source, no need for it so remove it.
                rup = get_rupture(origin, outfile)
                if isinstance(rup, PointRupture):
                    shutil.rmtree(outdir)

        new_file = 'events_comcat.csv'
        eq_df.to_csv(new_file, index=True)


if __name__ == '__main__':
    main()
