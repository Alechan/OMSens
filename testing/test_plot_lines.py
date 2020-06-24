import plotting.plot_specs as plot_specs
import pandas as pd
import unittest


class TestPlotLines(unittest.TestCase):

    # Tests:
    def test_class_creation(self):

        lower_line_spec = plot_specs.PlotLineSpecs(
            df=pd.DataFrame(),
            x_var='time',
            y_var='value',
            linewidth=1,
            linestyle='-',
            markersize=1,
            marker='o',
            label='label',
            color='c'
        )
        self.assertEquals(1, 1)
