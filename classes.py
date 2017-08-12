import numpy as np
import formencode
from formencode import validators


class StraightLine():
    """ A line in the form y = mx + b:

    Attributes:
        name: name of line
        gradient: slope of line (m)
        y_intercept: value of y at x=o (b)
    """

    def __init__(self, gradient, y_intercept):
        self.gradient = gradient
        self.y_intercept = y_intercept

        # validators.Empty.to_python(gradient)
        # validators.Number.to_python(gradient)

    def find_y_at_x(self, x_value):
        """ return the value of y at a given value of x

        """
        y_value = x_value * self.gradient + self.y_intercept
        return y_value

    def find_intercept_on_line(self, other_line):
        ''' finds the x value of intecept of self and another StraightLine

        '''
        m1 = self.gradient
        m2 = other_line.gradient

        if m1 != m2:
            b1 = self.y_intercept
            b2 = other_line.y_intercept
            x = (b1 - b2) / (m2 - m1)
        else:
            x = None  # no intercept for parallel lines (m1 = m2)
        return x

    def find_intercepts_on_line(self, other_lines):
        """ takes dict of other Straightline objects to return a
        dict of their x value of intecept on self.

        other_lines in the form {"other_line_name1": x1, "other_line_name2": x2 ...etc }

        """
        intercepts_on_line_dict = dict()
        for other_line in other_lines:
            intercepts_on_line_dict[other_line] = self.find_intercept_on_line(
                other_lines[other_line]
            )
        return intercepts_on_line_dict


class LoadDurationCurve():
    '''
    '''

    def __init__(self, curve_data, as_percent, as_proportion, granularity):
        self.curve_data = curve_data
        self.as_percent = as_percent
        self.as_proportion = as_proportion
        self.granularity = granularity

    def calculate_ldc_areas(self, generator_rank_list):
        '''
        '''

        # find start
        for x in [x_value[1] for x_value in generator_rank_list[1:]]:
            index = 0
            # print x
            for this_value, that_value in zip(self.curve_data[0][:-1], self.curve_data[0][1:]):
                # print this_value, that_value
                if x < this_value and x >= that_value:
                    print self.curve_data[1][index]
                index += 1


class PowerDemandTimeSeries():
    """ An uninterrupted time series of power demand

        Attributes:
        power_unit: units of power (options: W, MW, GW, TW)
        time_unit: time interval units (options: s, m, h, d)
        time_interval: number of time_units per time interval (float)
        demand_array: 1d numpy array of demand values over a period
    """

    def __init__(self, demand_array, power_unit, time_unit, time_interval):
        self.demand_array = np.array(demand_array)
        self.power_unit = power_unit
        self.time_unit = time_unit
        self.time_interval = time_interval

    def peak_demand(self):
        peak_demand = self.demand_array.max()
        return peak_demand

    def change_power_unit(self, new_power_unit):
        """ returns a new PowerDemandTimeSeries with power in newly specified units

        'W' = watts
        'MW' = megawatts
        'GW' = gigawatts
        'TW' = terawatts

        """
        power_unit_factors_dict = {
            'W': 1,
            'MW': 0.001,
            'GW': 0.000001,
            'TW': 0.000000001
        }
        demand_in_old_units = self.demand_array
        demand_in_new_units = power_unit_factors_dict[new_power_unit] * demand_in_old_units / power_unit_factors_dict[self.power_unit]
        return demand_in_new_units

    def create_load_duration_curve(self, as_percent=True, as_proportion=True, granularity=100):
        '''takes hourly demand data for a period
        returns a two np.arrays, one is list of demand levels
        other is list of time duration spent above those demand levels
        '''

        peak_demand = self.peak_demand()

        # create bins to sort data points
        demand_levels = (peak_demand / granularity) * np.array(range(0, granularity))

        # count data points above each bin and create list noting that count
        # list is the LDC

        duration_above_demand_level_list = list()
        for demand_level in demand_levels:
            count_above_demand_level = sum(self.demand_array >= demand_level)
            if as_proportion == True:
                proportion_above_demand_level = count_above_demand_level / float(len(self.demand_array))
                duration_above_demand_level_list.append(proportion_above_demand_level)
            else:
                duration_above_demand_level_list.append(count_above_demand_level)

        duration_above_demand_level_plot = np.append(np.array(duration_above_demand_level_list), 0)
        demand_levels_plot = np.append(demand_levels, peak_demand)
        if as_percent == True:
            curve_data = [duration_above_demand_level_plot, 100 * demand_levels_plot / peak_demand]

        else:
            curve_data = [duration_above_demand_level_plot, demand_levels_plot]
        load_duration_curve = LoadDurationCurve(
            curve_data=curve_data,
            as_percent=as_percent,
            as_proportion=as_proportion,
            granularity=granularity
        )
        return load_duration_curve
