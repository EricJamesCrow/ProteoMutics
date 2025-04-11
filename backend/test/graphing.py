import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks
import matplotlib.lines as mlines
from pathlib import Path

# Update the path in sys.path or configure your environment so that
# these imports resolve correctly for your pipeline
import sys
sys.path.append('/home/cam/Documents/repos/ProteoMutics/backend')
from app.utils import data_frame_operations, tools


class NucleosomeGrapher:
    # Define your color palettes at the class level
    colors_graph1 = ['#008B8B', '#960018']  # Dark Cyan, Carmine Red
    colors_graph2 = ['#4B0082', '#FF8C00', '#228B22']  # Indigo, Dark Orange, Forest Green

    def __init__(
        self,
        wt_total_file: str,
        wt_intersect_file: str,
        dyads_counts_file: str,
        genomic_counts_file: str,
        # Add any other initialization parameters if needed
    ):
        """
        Initialize the class with paths to your data files. 
        The constructor loads and prepares the data so that 
        plotting methods can be called directly.
        """

        # 1. Read in all data
        self.wt_total = data_frame_operations.DataFormatter.read_dataframe(wt_total_file)
        self.wt_intersect = data_frame_operations.DataFormatter.read_dataframe(wt_intersect_file)
        self.dyads_counts = data_frame_operations.DataFormatter.read_dataframe(dyads_counts_file)
        self.genomic_counts = data_frame_operations.DataFormatter.read_dataframe(genomic_counts_file)

        # Convert to Paths
        self.wt_total_file = Path(wt_total_file)
        self.wt_intersect_file = Path(wt_intersect_file)
        self.dyads_counts_file = Path(dyads_counts_file)
        self.genomic_counts_file = Path(genomic_counts_file)

        # 2. Reverse complement calls if needed
        # Uncomment if your pipeline requires this:
        # self.dyads_counts = data_frame_operations.DataFormatter.reverse_complement_positional_strand_conversion(self.dyads_counts)
        # self.genomic_counts = data_frame_operations.DataFormatter.reverse_complement_tri_counts(self.genomic_counts)

        # 3. Perform genome-wide normalization
        self.data_formatter = data_frame_operations.DataFormatter.genome_wide_normalization(
            self.wt_total, self.dyads_counts, self.genomic_counts, self.wt_intersect
        )

    @staticmethod
    def make_graph_matplotlib(ax, mutation_data: pd.DataFrame, title: str, smoothing_method: None = None, output_path: str = None):
        """
        Plot the "Mutations Across Nucleosomes" graph exactly as in your original code.
        """
        plt.style.use('seaborn-whitegrid')  # A clean style for the plot
        plt.rcParams['font.family'] = 'Arial'  # Set a global font family

        indexes = mutation_data.index.tolist()
        graph_values = [sum(mutation_data.loc[item]) for item in indexes]

        # Optionally: write the computed values to a CSV (as in your code)
        table = pd.DataFrame(graph_values, index=indexes)
        table.to_csv(output_path, sep='\t', header=False, index=True)
        print(f"Saved table to {output_path}")
        
        ax.set_xlim([-1000, 1000])  # Set the limits for the x-axis

        x = np.array(indexes)
        y = np.array(graph_values)

        # Smoothing / interpolation if requested
        if smoothing_method:
            x_smooth, y_smooth = tools.smooth_data(x, y, method=smoothing_method, window_size=301, poly_order=7)
            spline = make_interp_spline(x_smooth, y_smooth, k=3)
            x_spline = np.linspace(x_smooth.min(), x_smooth.max(), 10000)
            y_spline = spline(x_spline)
        else:
            spline = make_interp_spline(x, y, k=3)
            x_spline = np.linspace(x.min(), x.max(), 10000)
            y_spline = spline(x_spline)

        # Find periodicity
        overall_period, overall_confidence, overall_signal_to_noise = tools.find_periodicity(
            x_spline, y_spline, min_period=50
        )
        print(f"Overall period: {overall_period}, confidence: {overall_confidence}, signal to noise: {overall_signal_to_noise}")

        # Prepare for peak detection
        x_axis_range = 2000  # from -1000 to +1000
        num_data_points = 10000
        data_points_per_unit = num_data_points / x_axis_range

        desired_peak_width_x_units = overall_period // 7
        desired_peak_width_data_points = desired_peak_width_x_units * data_points_per_unit

        peak_distance = round(overall_period * 0.8 * data_points_per_unit)

        peaks, properties = find_peaks(
            y_spline, distance=peak_distance, width=desired_peak_width_data_points
        )
        if peaks.size > 0:
            peak_x_coordinates = x_spline[peaks]
        else:
            peak_x_coordinates = []

        # Adjust peak near zero
        if peaks.size > 0:
            closest_peak_index = np.argmin(np.abs(peak_x_coordinates))
            closest_peak_to_zero = peak_x_coordinates[closest_peak_index]

            if closest_peak_to_zero != 0:
                peak_x_coordinates[closest_peak_index] = 0

            peaks[closest_peak_index] = np.argmin(np.abs(x_spline - 0))

            # Filter out peaks within 73 units of zero
            valid_peak_indices = [
                i for i in range(len(peak_x_coordinates))
                if i == closest_peak_index or np.abs(peak_x_coordinates[i]) > 73
            ]
            peaks = peaks[valid_peak_indices]
            peak_x_coordinates = peak_x_coordinates[valid_peak_indices]

        def in_red_region(val):
            for peak in peak_x_coordinates:
                if peak - 73 <= val <= peak + 73:
                    return True
            return False

        # Plot data
        ax.scatter(x, y, marker='.', s=2, color='darkgrey', alpha=0.6)
        for i in range(1, len(x_spline)):
            if in_red_region(x_spline[i-1]) and in_red_region(x_spline[i]):
                ax.plot(x_spline[i-1:i+1], y_spline[i-1:i+1], color=NucleosomeGrapher.colors_graph1[0])
            else:
                ax.plot(x_spline[i-1:i+1], y_spline[i-1:i+1], color=NucleosomeGrapher.colors_graph1[1])

        # # Specific y-limit from your use-case
        # ax.set_ylim([-0.1, 0.2])

        ax.set_title(title, fontsize=20, weight='bold')
        ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)', fontsize=16, weight='bold')
        ax.set_ylabel(r'$\mathbf{log_{2}}\left(\frac{\mathbf{observed}}{\mathbf{expected}}\right)$', fontsize=16, weight='bold')
        ax.tick_params(axis='both', which='major', labelsize=12)

        # Create custom legend handles
        green_line = mlines.Line2D([], [], color=NucleosomeGrapher.colors_graph1[0], markersize=15, label='Nucleosomal DNA')
        orange_line = mlines.Line2D([], [], color=NucleosomeGrapher.colors_graph1[1], markersize=15, label='Linker DNA')

        # Add custom legend
        ax.legend(
            handles=[green_line, orange_line],
            loc='upper right', fontsize=12,
            framealpha=0.5, facecolor='white', edgecolor='black', frameon=True,
            borderpad=0.2, labelspacing=0.2, handletextpad=0.2
        )

    @staticmethod
    def make_73_graph_matplotlib(ax, mutation_data: pd.DataFrame, title: str, smoothing_method: str = None):
        """
        Plot the "Mutations Within Nucleosomes" graph exactly as in your original code.
        """
        plt.style.use('seaborn-whitegrid')
        plt.rcParams['font.family'] = 'Arial'

        # Filter the data for the desired range (-72 to +72)
        mutation_data = mutation_data[(mutation_data.index >= -72) & (mutation_data.index <= 72)]

        ax.set_xlim([-72, 72])

        indexes = mutation_data.index.tolist()
        graph_values = [sum(mutation_data.loc[item]) for item in indexes]

        x = np.array(indexes)
        y = np.array(graph_values)

        # 2nd order polynomial fit
        poly_coeffs = np.polyfit(x, y, 2)
        poly_func = np.poly1d(poly_coeffs)
        poly_y = poly_func(x)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        trend_y = intercept + slope * x

        # Print lines for debug
        print(f"Linear trend line: y = {slope:.2f}x + {intercept:.2f}")
        print(f"Polynomial trend line: y = {poly_coeffs[0]:.2f}x^2 + {poly_coeffs[1]:.2f}x + {poly_coeffs[2]:.2f}")

        if smoothing_method:
            x_smooth, y_smooth = tools.smooth_data(x, y, method=smoothing_method, window_size=5, poly_order=3)
            spline = make_interp_spline(x_smooth, y_smooth, k=3)
            x_spline = np.linspace(x_smooth.min(), x_smooth.max(), 10000)
            y_spline = spline(x_spline)
            ax.plot(x_spline, y_spline, color='black', label='Smoothed Curve', lw=1)
        else:
            # If no smoothing, just use the raw data for peak detection
            x_spline = x
            y_spline = y

        # Periodicity
        overall_period, overall_confidence, overall_signal_to_noise = tools.find_periodicity(
            x, y, min_period=2, max_period=25
        )
        print(f"Overall period: {overall_period}, confidence: {overall_confidence}, signal to noise: {overall_signal_to_noise}")

        peak_distance = round(overall_period * 0.8)

        x_axis_range = 72 - (-72)  # 144 units
        num_data_points = 10000
        data_points_per_unit = num_data_points / x_axis_range

        desired_peak_width_x_units = overall_period // 3
        desired_peak_width_data_points = desired_peak_width_x_units * data_points_per_unit

        # If smoothing isn't used, we still want a spline for peak detection
        if len(x_spline) != len(y_spline):
            # Create a spline over the raw data
            x_spline = np.linspace(x.min(), x.max(), 10000)
            spline2 = make_interp_spline(x, y, k=3)
            y_spline = spline2(x_spline)

        # Find peaks and valleys
        peaks, properties = find_peaks(y_spline, distance=peak_distance, width=desired_peak_width_data_points)
        if peaks.size > 0:
            peak_x_coordinates = x_spline[peaks]
        else:
            peak_x_coordinates = []

        valleys, properties = find_peaks(-y_spline, distance=peak_distance, width=desired_peak_width_data_points)
        if valleys.size > 0:
            valley_x_coordinates = x_spline[valleys]
        else:
            valley_x_coordinates = []

        # Segment coloring
        def color_segment(start, end, color):
            mask = (x_spline >= start) & (x_spline <= end)
            ax.plot(x_spline[mask], y_spline[mask], color=color, lw=2)

        combined_points = np.concatenate((peak_x_coordinates, valley_x_coordinates))
        sorted_points = np.sort(combined_points)
        midpoints = (sorted_points[:-1] + sorted_points[1:]) / 2
        midpoints = np.append(midpoints, [-72, 72])
        midpoints = np.sort(midpoints)

        zero_index = None
        # Color the segment containing zero in a distinct color first
        for i in range(len(midpoints) - 1):
            if midpoints[i] <= 0 <= midpoints[i + 1]:
                color_segment(midpoints[i], midpoints[i + 1], NucleosomeGrapher.colors_graph2[0])
                zero_index = i
                break

        # Color the remaining segments alternatingly
        if zero_index is not None:
            # To the left of zero
            green = True
            for i in range(zero_index, 0, -1):
                color_segment(
                    midpoints[i - 1],
                    midpoints[i],
                    NucleosomeGrapher.colors_graph2[1] if green else NucleosomeGrapher.colors_graph2[0]
                )
                green = not green

            # To the right of zero
            green = False
            for i in range(zero_index + 1, len(midpoints) - 1):
                color_segment(
                    midpoints[i],
                    midpoints[i + 1],
                    NucleosomeGrapher.colors_graph2[1] if green else NucleosomeGrapher.colors_graph2[0]
                )
                green = not green

        # Plot the raw data and polynomial fit
        ax.scatter(x, y, marker='.', s=10, color='darkgrey', alpha=0.6, label='Original Data')
        ax.plot(x, poly_y, color=NucleosomeGrapher.colors_graph2[2], label='Polynomial Fit', linestyle='--')

        # # Specific y-limit
        # ax.set_ylim([-0.2, 0.4])

        ax.set_title(title, fontsize=20, weight='bold')
        ax.set_xlabel('Nucleotide Position Relative to Nucleosome Dyad (bp)', fontsize=16, weight='bold')
        ax.set_ylabel(r'$\mathbf{log_{2}}\left(\frac{\mathbf{observed}}{\mathbf{expected}}\right)$', fontsize=16, weight='bold')
        ax.tick_params(axis='both', which='major', labelsize=12)

        # Create custom legend handles
        green_line = mlines.Line2D([], [], color=NucleosomeGrapher.colors_graph2[1], markersize=15, label='Inward Facing DNA')
        orange_line = mlines.Line2D([], [], color=NucleosomeGrapher.colors_graph2[0], markersize=15, label='Outward Facing DNA')
        blue_line = mlines.Line2D([], [], color=NucleosomeGrapher.colors_graph2[2], markersize=15, linestyle='--', label='Binomial Fit')

        # Add custom legend handles
        ax.legend(
            handles=[green_line, orange_line, blue_line],
            loc='upper right', fontsize=12,
            framealpha=0.5, facecolor='white', edgecolor='black', frameon=True,
            borderpad=0.2, labelspacing=0.2, handletextpad=0.2
        )

    def plot_nucleosome_graphs(self, smoothing_method='savgol_filter', show_plot=True, save_path=None):
        """
        Public method that creates and renders both subplots:

        1) 'Mutations Across Nucleosomes'  (full -1000 to +1000)
        2) 'Mutations Within Nucleosomes'  (zoomed -72 to +72)

        :param smoothing_method: The smoothing method to pass to the chart functions.
        :param show_plot: If True, calls plt.show() at the end.
        :param save_path: If provided, saves the figure to the given path (e.g., 'output.png').
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

        # Plot using the static methods
        out_file = self.wt_total_file.with_suffix(".nucleosome_counts")
        self.make_graph_matplotlib(ax1, self.data_formatter, 'Mutations Across Nucleosomes', smoothing_method, out_file)
        self.make_73_graph_matplotlib(ax2, self.data_formatter, 'Mutations Within Nucleosomes', smoothing_method)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Saved figure to {save_path}")

        if show_plot:
            plt.show()


if __name__ == "__main__":
    # Example usage:
    # Initialize the NucleosomeGrapher with paths to your data files
    grapher = NucleosomeGrapher(
        wt_total_file="backend/test/test_data/UV_nucleomutics/UV.counts",
        wt_intersect_file="backend/test/test_data/UV_nucleomutics/UV_hg19_MNase_nucleosome_map_all.intersect",
        dyads_counts_file="/media/cam/Storage/8-oxodG/hmces/nucleosome/hg19_MNase_nucleosome_map_all_proteomutics/hg19_MNase_nucleosome_map_all.counts",
        genomic_counts_file="/home/cam/Documents/repos/ProteoMutics/backend/test/test_data/hg19.counts",
    )
    grapher.plot_nucleosome_graphs(
        smoothing_method='savgol_filter',
        show_plot=True,
        save_path=None
    )