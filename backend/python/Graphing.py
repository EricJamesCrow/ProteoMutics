import Tools
from pathlib import Path
import matplotlib.pyplot as plt, mpld3
import numpy as np
import pandas as pd

def make_graph(mutation_data: pd.DataFrame, interpolate_method: None | bool = False, smoothing_method: str | None = None):
    indexes = mutation_data.index.tolist()
    graph_values = []
    for item in indexes:
        graph_values.append(sum(mutation_data.loc[item]))
    x = np.array(indexes)
    y = np.array(graph_values)
    # if smoothing data, apply smoothing method
    if smoothing_method:
        x, y = Tools.smooth_data(x, y, method = smoothing_method)
    # if interpolating missing data, apply method and adjust values
    if interpolate_method:
        x, y = Tools.interpolate_missing_data(x, y, -1000, 1000, interpolate_method)
    # setting up matplotlib object
    fig, ax = plt.subplots()
    ax.scatter(x, y, marker='.', s=1, linewidths=1)
    # Define the x-domain of interest for the nucleosome
    xmin = -73
    xmax = 73
    # Create a mask to select the x-values in the specified domain
    mask = (x >= xmin) & (x <= xmax)

    # Plot the line segments connecting each data point in the domain
    for i in range(len(x)-1):
        if mask[i] and mask[i+1]:
            ax.plot([x[i], x[i+1]], [y[i], y[i+1]], color='red', lw=2)

    # Plot the line segments for the outer domain
    outer_minus_mask = (x <= xmin)
    outer_plus_mask = (x >= xmax)
    for i in range(len(x)-1):
        if outer_minus_mask[i] and outer_minus_mask[i+1]:
            ax.plot([x[i], x[i+1]], [y[i], y[i+1]], color='blue', lw=2)
        if outer_plus_mask[i] and outer_plus_mask[i+1]:
            ax.plot([x[i], x[i+1]], [y[i], y[i+1]], color='blue', lw=2)

    # Set the x-axis and y-axis labels
    ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)')
    ax.set_ylabel('Mutation Counts Normalized to Context')

    # Set the title of the plot
    ax.set_title('Nucleomutics!')

    # Disable scientific notation on the x-axis
    ax.ticklabel_format(axis='x', style='plain')

    # add gridlines
    ax.grid(True)
    return fig

def save_figure(graph_object: tuple, dpi: int, fig_output_name: str):
    # finish me pls
    plt.savefig(graph_object, dpi = dpi, )

def display_figure(graph_object):
    html_obj = mpld3.fig_to_html(graph_object)
    return html_obj