import numpy
import matplotlib
matplotlib.use("Agg") # Agg backend does not require an X server
import matplotlib.pyplot as plt
from os.path import join

import stats
import utils

def bar_chart(data, labels, output,
              title='Bar Chart', xlabel='x', ylabel='y', xmul=1, ymul=1):
    """Makes a bar chart.
    (never used)"""
    N = len(labels)

    # we have a generator full of tuples. if we were to make that into a
    # 2d array, we would have to transpose it for it to unpack properly
    # either do as a numpy array, or find some way to do it with itertools.
    # I tried just using zip on it, but that didn't work
    means, stds, mins, maxs = numpy.transpose(numpy.vstack(
        tuple(stats.summary(d) for d in data)))
    
    # # there's probably a way to do this much better with zip
    # means = ymul*numpy.fromiter((data[k]["mean"] for k in keys), numpy.float)
    # stds  = ymul*numpy.fromiter((data[k]["std" ] for k in keys), numpy.float)
    # mins  = ymul*numpy.fromiter((data[k]["min" ] for k in keys), numpy.float)
    # maxs  = ymul*numpy.fromiter((data[k]["max" ] for k in keys), numpy.float)

    x_offsets = numpy.arange(N)
    width = 0.22

    fig, ax = plt.subplots()
    min_rects = ax.bar(x_offsets, mins, width,
                       color='b', label='min')
    mean_rects = ax.bar(x_offsets+width, means, width,
                        color='r', yerr=stds, label='mean')
    max_rects = ax.bar(x_offsets+(2*width), maxs, width,
                       color='y', label='max')

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x_offsets+(1.5*width))
#    ax.set_xticklabels(numpy.fromfunction(
#        function=lambda i: str(xmul*keys[i]), shape=(N,)))
    ax.set_xticklabels(list(map(str, xmul*labels)))

    # shrink the axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # place legend outside of axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig(join(output, title.replace(' ', '_') + ".png"), dpi=500)

def box_plot(data, labels, output,
             title='Box Plot', xlabel='x', ylabel='y', xmul=1, ymul=1):
    """Makes a box plot"""
    N = len(labels)
    x_offsets = numpy.arange(N)
    
    fig, ax = plt.subplots()

    ax.boxplot(list(ymul*data))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(list(map(lambda x: str(int(x)), xmul*labels)))

    plt.savefig(join(output, title.replace(' ', '_') + ".png"), dpi=500)
