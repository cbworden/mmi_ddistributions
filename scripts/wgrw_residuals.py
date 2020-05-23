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
    Analyze WGRW12 residuals.
    """
    imts = [i[0] for i in get_data.IMTS]

    # Make some histograms
    for imt in imts:
        fig = plt.figure(figsize=(5, 5))
        ax = mmi_histogram(imt)
        fig.add_axes(ax)
        fig_name = os.path.join(
            FIG_DIR, 'mmi_residual_histogram_%s.png' % imt)
        fig.savefig(fig_name, dpi=300)


def mmi_histogram(imt='pgv'):
    mmi_residuals = SHAKE_DF['mmi_res_%s' % imt]
    mmi_res_mean = np.mean(mmi_residuals)
    mmi_res_sd = np.std(mmi_residuals)

    ax = sns.distplot(mmi_residuals, kde=False, norm_hist=True)
    mmi_grid = np.linspace(np.min(mmi_residuals), np.max(mmi_residuals), 300)
    normal_pdf = stats.norm.pdf(mmi_grid, mmi_res_mean, mmi_res_sd)
    ax.plot(mmi_grid, normal_pdf, 'k', lw=2)
    ax.set_xlabel('MMI from %s residual' % imt.upper())
    ax.set_ylabel('MMI residual PDF')
    ax.set_title('Sample mean and std: %.3f, %.3f' %
                 (mmi_res_mean, mmi_res_sd))
    return ax


if __name__ == '__main__':
    main()
