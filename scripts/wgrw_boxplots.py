#!/usr/bin/env python

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sys.path.append(os.path.join('..', 'data'))
import get_data

# Read in the data
SHAKE_DF = get_data.read_shake_data()

FIG_DIR = os.path.join('..', 'figs')


def main():
    """
    Analyze converted MMI values and how the distribution changes with
    predicted MMI.
    """
    imts = [i[0] for i in get_data.IMTS]

    # Make some histograms
    for imt in imts:
        fig = plt.figure(figsize=(5, 5))
        ax = mmi_boxplots(imt)
        fig.add_axes(ax)
        fig_name = os.path.join(
            FIG_DIR, 'mmi_residual_boxplots_%s.png' % imt)
        fig.savefig(fig_name, dpi=300)


def mmi_boxplots(imt='pgv'):
    mmi = np.array(SHAKE_DF['mmi'])

    mmi_pred = np.array(SHAKE_DF['mmi_from_%s' % imt])
    mmi_pred_int = np.array(np.round(mmi_pred, 0), dtype=int)
    ax = sns.boxplot(mmi_pred_int, mmi, color='w')
    diagl = np.array([1, 9])
    # needs to shift to left by 1 unit??????
    ax.plot(diagl - 1, diagl, 'k--')
    ax.set_xlabel('Predicted MMI (nearest integer)')
    ax.set_ylabel('Observed MMI')
    ax.set_title('MMI converted from %s' % imt.upper())
    return ax


if __name__ == '__main__':
    main()
