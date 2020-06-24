# Std
import six
import pandas

# Mine
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging
from random import sample
import plotting.plot_specs as plot_specs
import numpy as np
import pandas as pd

filehandler = logging.FileHandler("/home/omsens/Documents/results_experiments/logging/todo.log")
logger = logging.getLogger("plot_in_folder")
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)


class LinesPlotter:
    def __init__(self, plot_specs):
        logger.debug('start init lines plotter')
        self.plot_specs = plot_specs
        self.MAX_LINES_IN_PLOT = 3000
        logger.debug('end init lines plotter')

    def plotInPath(self, plot_path_without_extension, with_upper_and_lower=False):
        try:
            logger.debug("Enter plotInPath")

            footer_artist = setupPlot(self.plot_specs.setup_specs)

            # logger.debug("plot lines")
            ls = self.plot_specs.lines_specs
            ls = sample(ls, self.MAX_LINES_IN_PLOT) if len(ls) > self.MAX_LINES_IN_PLOT else ls
            for line_spec in ls:
                plotLineSpec(line_spec)

            # Add upper and lower bound lines to plot
            if with_upper_and_lower:
                plotUpperLowerAndMeanLines(ls)
            # Define legend
            logger.debug("set legend")
            lgd = plt.legend(loc="center left", fontsize="small",
                             fancybox=True, shadow=True,
                             bbox_to_anchor=(1, 0.5))

            logger.debug("setup xticks")
            setupXTicks(self.plot_specs.setup_specs.extra_ticks)
            logger.debug("FInish setup x ticks")
            saveAndClearPlt(plot_path_without_extension, lgd, footer_artist)
            logger.debug("finish save and clear plt")
            return 0
        except Exception:
            return 1


def plotUpperLowerAndMeanLines(ls_line_specs):
    # logger.debug("plotting upper and lower 1")
    # Initialize upper and lower bounds: Create new columns with maximum and minimum values of variables
    lower_line = {'df': None, 'x_var': 'time', 'y_var': 'minimum', 'linestyle': '-',
                  'linewidth': 2, 'markersize': 0, 'marker': 'o', 'label': 'Lower', 'color': 'blue'}
    upper_line = {'df': None, 'x_var': 'time', 'y_var': 'maximum', 'linestyle': '-',
                  'linewidth': 2, 'markersize': 0, 'marker': 'o', 'label': 'Upper', 'color': 'red'}
    mean_line = {'df': None, 'x_var': 'time', 'y_var': 'mean', 'linestyle': '-',
                  'linewidth': 1.5, 'markersize': 0, 'marker': 'o', 'label': 'Mean', 'color': 'black'}

    # logger.debug("plotting upper and lower 2")
    df = None
    # Update / Initialize upper and lower line specs
    for i, line_spec in enumerate(ls_line_specs):
        # Continue
        if df is None:
            df = line_spec.df[['time', line_spec.y_var]].copy().rename(columns={line_spec.y_var: line_spec.y_var + '_' + str(i)})
        else:
            df = pd.merge(df, line_spec.df[['time', line_spec.y_var]], on='time', how='left').rename(columns={line_spec.y_var: line_spec.y_var + '_' + str(i)})

    # debug
    cols = [c for c in df.columns if c not in ['time']]

    # logger.debug("plotting upper and lower 3")
    # logger.debug("cols: %s" % str(cols))

    def get_statistics(row):
        vals = row.values
        return pd.Series([min(vals), np.mean(vals), max(vals)])

    # logger.debug(df.columns.tolist())
    # logger.debug(df.head())
    df[['minimum', 'mean', 'maximum']] = df[cols].apply(get_statistics, 1)
    # logger.debug(df[['minimum', 'mean', 'maximum']].head())

    # logger.debug("plotting upper and lower 4")

    mean_line['df'] = df[['time', 'mean']]
    lower_line['df'] = df[['time', 'minimum']]
    upper_line['df'] = df[['time', 'maximum']]

    # logger.debug("plotting upper and lower 5")

    # Generate Upper/Lower Lines and plot.
    lower_line_spec = plot_specs.PlotLineSpecs(**lower_line)
    plotLineSpec(lower_line_spec)
    upper_line_spec = plot_specs.PlotLineSpecs(**upper_line)
    plotLineSpec(upper_line_spec)
    mean_line_spec = plot_specs.PlotLineSpecs(**mean_line)
    plotLineSpec(mean_line_spec)
    logger.debug("plotting upper and lower 6")

    return 0


def plotLineSpec(line_spec):
    x_data = xDataForLineSpec(line_spec)
    y_data = line_spec.df[line_spec.y_var]

    linewidth = line_spec.linewidth
    linestyle = line_spec.linestyle
    markersize = line_spec.markersize
    marker = line_spec.marker
    label = line_spec.label
    color = line_spec.color

    # Call plotting function
    plt.plot(x_data, y_data,
             linewidth=linewidth,
             linestyle=linestyle,
             markersize=markersize,
             marker=marker,
             label=label,
             color=color)


def xDataForLineSpec(line_spec):
    # Check if its a column or the index
    if line_spec.x_var:
        x_data = line_spec.df[line_spec.x_var]
    else:
        # If no column is included, return the index
        index = line_spec.df.index
        x_data = tryTimestampOrNumberForList(index)
    return x_data


def tryTimestampOrNumberForList(orig_index):
    # There's no way in python to ask if an object is a number, so we just try
    # to use it as a timestamp and if it fails then it's a number
    try:
        # For now, we just assume that if it's not an int, it's a timestamp that knows to respond to "year"
        final_index = [x.year for x in orig_index]
    except AttributeError:
        # If it can't respond to year, ask if it's a string
        # Get the first cell
        first_cell = orig_index[0]
        if isinstance(first_cell, six.string_types):
            # If it's a string, assume it's a timestamp and convert it to pandas datetime
            orig_index_datetime = pandas.to_datetime(orig_index)
            # Get the year from the timestamp
            final_index = [x.year for x in orig_index_datetime]
        else:
            # Assume it's a number and matplotlib can plot it
            final_index = orig_index
    return final_index


def setupPlot(setup_specs):
    plt.style.use('fivethirtyeight')
    plt.gca().set_position([0.10, 0.15, 0.80, 0.77])
    plt.xlabel(setup_specs.x_label)
    plt.title(setup_specs.title + "\n" + setup_specs.subtitle, fontsize=14, y=1.08)
    plt.ylabel(setup_specs.y_label)
    plt.ticklabel_format(useOffset=False)  # So it doesn't use an offset on the x axis
    footer_artist = plt.annotate(setup_specs.footer, (1, 0), (0, -70), xycoords='axes fraction',
                                 textcoords='offset points',
                                 va='top', horizontalalignment='right')
    plt.margins(x=0.1, y=0.1)  # increase buffer so points falling on it are plotted
    return footer_artist


def setupXTicks(extra_ticks):
    # Get the ticks automatically generated by matplotlib
    auto_x_ticks = list(plt.xticks()[0])
    # Trim the borders (excessively large)
    auto_x_ticks_wo_borders = auto_x_ticks[1:-1]
    x_ticks = sorted(auto_x_ticks_wo_borders + extra_ticks)
    # plt.xticks(x_ticks, rotation='vertical')  # add extra ticks (1975 for vermeulen for example)
    plt.xticks(x_ticks, rotation='horizontal')


def saveAndClearPlt(plot_path_without_extension, lgd, footer_artist, extra_lgd=None):
    logger.debug('SAVE AND CLEAR PLOT')
    extensions = [".png"]
    for ext in extensions:
        plot_path = plot_path_without_extension + ext
        logger.debug(plot_path)
        logger.debug(extra_lgd)
        if extra_lgd:
            # If two legends (for when the plot has variables with different scale)
            logger.debug('two legends')
            plt.savefig(plot_path, bbox_extra_artists=(lgd, extra_lgd, footer_artist), bbox_inches='tight')
        else:
            # If only one legend
            logger.debug('only 1 legend')
            plt.savefig(plot_path, bbox_extra_artists=(lgd, footer_artist), bbox_inches='tight')
    logger.debug('finish0')
    plt.clf()
    logger.debug('finish1')
