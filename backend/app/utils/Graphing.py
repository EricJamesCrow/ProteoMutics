from . import Tools
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo

def make_graph(mutation_data: pd.DataFrame, interpolate_method: bool = False, smoothing_method: None = None):
    indexes = mutation_data.index.tolist()
    graph_values = []
    for item in indexes:
        graph_values.append(sum(mutation_data.loc[item]))
    x = np.array(indexes)
    y = np.array(graph_values)
    # within a nucleosome
    period, confidence, signal_to_noise = Tools.find_periodicity(x, y, 10.2)
    # between nucleosomes
    overall_period, overall_confidence, overall_signal_to_noise = Tools.find_periodicity(x, y, 300)
    # if smoothing data, apply smoothing method
    if smoothing_method:
        x, y = Tools.smooth_data(x, y, method=smoothing_method)
    # if interpolating missing data, apply method and adjust values
    if interpolate_method:
        x, y = Tools.interpolate_missing_data(x, y, -1000, 1000, interpolate_method)

    # Identify peaks based on overall_period
    peaks = [0]  # first peak is at 0

    # Handle right side of the graph
    while peaks[-1] + overall_period < x[-1]:
        peaks.append(peaks[-1] + overall_period)

    # Handle left side of the graph
    while peaks[0] - overall_period > x[0]:
        peaks.insert(0, peaks[0] - overall_period)

    # Define a function to check if a value is within a red region
    def in_red_region(val):
        for peak in peaks:
            if peak - 73 <= val <= peak + 73:
                return True
        return False

    # Create the scatter plot
    scatter_trace = go.Scattergl(x=x, y=y, mode='markers', marker=dict(size=2, color='black'), name='Mutation Counts')

    # Create the line segments for the domain and outer domain
    line_traces = []
    for i in range(len(x) - 1):
        color = 'red' if in_red_region(x[i]) or in_red_region(x[i + 1]) else 'blue'
        line_traces.append(go.Scattergl(x=x[i:i + 2], y=y[i:i + 2], mode='lines', line=dict(color=color, width=2)))

    # Combine all the traces
    traces = [scatter_trace] + line_traces

    # Set the layout of the plot
    layout = go.Layout(
        title='Proteomutics!',
        xaxis=dict(title='Nucleotide Position Relative to Nucleosome Dyad (bp)'),
        yaxis=dict(title='Mutation Counts Normalized to Context'),
        showlegend=False,
        width=750,
        height=375
    )

    # Create the Figure object
    fig = go.Figure(data=traces, layout=layout)

    return fig, period, confidence, signal_to_noise

def save_figure(graph_object: go.Figure, dpi: int, fig_output_name: str):
    graph_object.write_image(fig_output_name, scale=dpi/72, format='svg')

def display_figure(graphing_data_tuple: tuple):
    graph_object, period, confidence, signal_to_noise = graphing_data_tuple
    graph_object = pyo.plot(graph_object, include_plotlyjs=False, output_type='div')
    period, confidence, signal_to_noise = ["{:.3f}".format(num) for num in [period, confidence, signal_to_noise]]
    return (graph_object, period, confidence, signal_to_noise)
