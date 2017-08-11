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

    def find_intercepts_on_line(self, other_lines):
        """returns a dict of the coordinates of the intersection of this line with 
        other lines in the form {"other_line_name1": x1, "other_line_name2": x2 ...etc }

        """
        intercepts_on_line_dict = dict()
        for other_line in other_lines:
            m1 = self.gradient
            m2 = other_lines[other_line].gradient
            b1 = self.y_intercept
            b2 = other_lines[other_line].y_intercept
            x = (b1 - b2) / (m2 - m1)
            intercepts_on_line_dict[other_line] = x
        return intercepts_on_line_dict


class PowerDemandTimeSeries():
    """ An uninterrupted time series of power demand

        Attributes:
        power_unit: units of power (options: W, MW, GW, TW)
        time_unit: time interval units (options: s, m, h, d)
        time_interval: number of time_units per time interval (float)
        demand_array: numpy array of demand values where index represents time interval
    """

    def __init__(self, demand_array, power_unit, time_unit, time_interval):
        self.demand_array = np.array(demand_array)
        self.power_unit = power_unit
        self.time_unit = time_unit
        self.time_interval = time_interval

    def change_power_unit(self, new_power_unit):
        """ returns a new PowerDemandTimeSeries with power in newly specified units

        'W' = watts
        'MW' = megawatts
        'GW' = gigawatts
        'TW' = terawatts

        """
        power_unit_options_dict = {'W': 1, 'MW': 1000, 'GW': 1000000, 'TW': 1000000000}
        demand_in_old_units = self.demand_array
        demand_in_new_units = (demand_in_old_units * power_unit_options_dict[self.power_unit]) / power_unit_options_dict[new_power_unit]
        return demand_in_new_units

    # def change_time_unit(self, new_time_unit):
    #     """ returns a new PowerDemandTimeSeries with time in newly specified units

    #     's' = seconds
    #     'm' = minutes
    #     'h' = hours
    #     'd' = days
    #     """

    # def change_time_interval():
