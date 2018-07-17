"""
Accompanying source to "Python Plotting With Matplotlib (Guide)"

Note: charts in "Python Plotting With Matplotlib (Guide)" were
generated using a custom matplotlibrc file.

Outputs may look different stylistically using default matplotlib styling.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

import numpy as np

np.random.seed(444)


def main():
    x = np.diag(np.arange(2, 12))[::-1]
    x[np.diag_indices_from(x[::-1])] = np.arange(2, 12)
    x2 = np.arange(x.size).reshape(x.shape)

    sides = ('left', 'right', 'top', 'bottom')
    nolabels = {s: False for s in sides}
    nolabels.update({'label%s' % s: False for s in sides})

    with plt.rc_context(rc={'axes.grid': False}):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
        ax1.matshow(x)
        img2 = ax2.matshow(x2, cmap='RdYlGn_r')
        for ax in (ax1, ax2):
            ax.tick_params(axis='both', which='both', **nolabels)
        for i, j in zip(*x.nonzero()):
            ax1.text(j, i, x[i, j], color='white', ha='center', va='center')
        divider = make_axes_locatable(ax2)
        cax = divider.append_axes("right", size='5%', pad=0)
        plt.colorbar(img2, cax=cax, ax=[ax1, ax2])
        fig.suptitle('Heatmaps with `Axes.matshow`', fontsize=16)


if __name__ == '__main__':
    plt.ioff()
    main()
    plt.show()
