import numpy as np
import numbers
import pandas as pd
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt


class StraightLine(object):
    """ A line in the form y = mx + b:

    Attributes:
        name: name of line
        gradient: value of slope of line (m)
        y_intercept: value of y at x=0 (b)
        x_range: range over which line exists as [x1, x2] (e.g. [2,6])
    """

    def __init__(self, gradient, y_intercept, x_range=None):
        self.gradient = gradient
        self.y_intercept = y_intercept
        self.x_range = x_range

        if not isinstance(gradient, numbers.Number):
            raise ValueError('gradient must be a number')
        if not isinstance(y_intercept, numbers.Number):
            raise ValueError('y_intercept must be a number')

    def find_y_at_x(self, x_value):
        """ return the value of y at a given value of x

        """
        if not isinstance(x_value, numbers.Number):
            raise ValueError('x_value argument must be a number')

        y_value = x_value * self.gradient + self.y_intercept
        return y_value

    def find_intercept_on_line(self, other_line):
        ''' finds the x value of intecept of self and another StraightLine

        '''
        if not isinstance(other_line, StraightLine):
            raise ValueError('other_line must be StraightLine objects')

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

        # MAKE LIST INPUT OPTION??

        """
        if not isinstance(other_lines, dict):
            raise ValueError("other_lines must be dictionary with other line's names as keys and StraightLine objects as values")

        intercepts_on_line_dict = dict()
        for other_line in other_lines:
            intercepts_on_line_dict[other_line] = self.find_intercept_on_line(
                other_lines[other_line]
            )
        return intercepts_on_line_dict


class LoadDurationCurve():
    '''
    '''

    def __init__(self, curve_data, as_percent, peak_demand, as_proportion, granularity):
        self.curve_data = curve_data
        self.as_percent = as_percent
        self.peak_demand = peak_demand
        self.as_proportion = as_proportion
        self.granularity = granularity

    def locate_y_at_x(self, x_value, return_index=False):
        '''
        '''
        index = 0
        for this_value, that_value in zip(self.curve_data[0][:-1], self.curve_data[0][1:]):
            if x_value < this_value and x_value >= that_value:
                if return_index:
                    return {'y': self.curve_data[1][index], 'index': index}
                    break
                else:
                    return self.curve_data[1][index]
                    break
            elif x_value == this_value and x_value == that_value:
                if return_index:
                    return {'y': 0, 'index': 0}
                else:
                    return 0
            index += 1

    def calculate_ldc_section_area(self, x_values):
        '''
        '''
        start_position = self.locate_y_at_x(x_values[1], return_index=True)
        start_position_slice = start_position['index']
        finish_position = self.locate_y_at_x(x_values[0], return_index=True)
        finish_position_slice = finish_position['index']
        curve_interval_x_list = zip(
            self.curve_data[0][start_position_slice:(finish_position_slice - 1)],
            self.curve_data[0][(start_position_slice + 1): finish_position_slice])
        if self.as_percent:
            # y_deltas are all same
            y_delta = self.peak_demand * (self.curve_data[1][1] - self.curve_data[1][0])
        else:
            y_delta = self.curve_data[1][1] - self.curve_data[1][0]
        cumulative_area = 0
        count = 0
        for interval_start_x, interval_finish_x in curve_interval_x_list:
            # calculate interval area
            interval_area = y_delta * (interval_start_x + interval_finish_x) / 2
            cumulative_area += interval_area
            count += 1
        if self.as_proportion:
            return cumulative_area * 8760
        else:
            return cumulative_area

    def required_capacities(self, generator_rank_list):
        ''' determine required capacities and amount of electricity produced
            per year by each generator in rank list
        '''
        change_back_to_as_percent = False
        if self.as_percent:
            self.curve_data = self.curve_data * self.peak_demand
            self.as_percent = False
            change_back_to_as_percent = True

        required_capacities_dict = dict()
        y_values_list = list()

        for i, generator in enumerate(generator_rank_list[:-1]):
            y_value1 = self.locate_y_at_x(generator_rank_list[i][1])
            y_value2 = self.locate_y_at_x(generator_rank_list[i + 1][1])
            y_values_list.append((generator[0], y_value1, y_value2))
        y_value_1 = self.locate_y_at_x(generator_rank_list[-1][1])
        y_values_list.append((generator_rank_list[-1][0], y_value_1, self.peak_demand))

        for y_val in y_values_list:
            required_capacities_dict[y_val[0]] = y_val[2] - y_val[1]
        if change_back_to_as_percent:
            self.as_percent = True
        return required_capacities_dict


class PowerDemandTimeSeries():
    """ An uninterrupted time series of power demand

        Attributes:
        power_unit: units of power (options: W, MW, GW, TW)
        time_unit: time interval units (options: s, m, h, d)
        time_interval: number of time_units per time interval (float)
        demand_array: 1d numpy array of demand values over a period
    """

    def __init__(
        self,
        demand_array,
        power_unit,
        time_unit,
        time_interval=1,
        start_datetime=None,
        start_date_and_time=None
    ):
        '''
        power_unit:
        'W' = watts
        'kW' = kilowatts
        'MW' = megawatts
        'GW' = gigawatts
        'TW' = terawatts

        start_datetime: datetime object
        start_date_and_time: (yyyy, mm, dd, h, m, s, ms)
        '''

        self.demand_array = np.array(demand_array)
        self.power_unit = power_unit
        self.time_unit = time_unit
        self.time_interval = time_interval
        self.start_datetime = start_datetime
        self.start_date_and_time = start_date_and_time

        if self.start_datetime and self.start_date_and_time:
            raise ValueError('you may sepcify either start_datetime OR start_date_and_time, not both')

        if self.start_datetime:
            if not isinstance(self.start_datetime, datetime.datetime):
                raise ValueError('start_datetime must be datetime object. Alternatively you may enter the start_date_and_time parameter as tuple in the form (year, month, day, hour, minute, second, microsecond). If you choose to enter neither, the default start date will be (1900, 1, 1, 0, 0, 0, 0)')

        if self.time_unit not in ['microseconds', 'milliseconds', 'seconds', 'minutes', 'hours', 'days', 'weeks']:
            raise ValueError('time_unit must be set as either "microseconds", "milliseconds", "seconds", "minutes", "hours", "days" or "weeks"')

    def create_datetime_series(self):

        if self.start_datetime:
            base_datetime = self.start_datetime
        elif self.start_date_and_time:
            year = self.start_date_and_time[0]
            month = self.start_date_and_time[1]
            day = self.start_date_and_time[2]
            hour = self.start_date_and_time[3]
            minute = self.start_date_and_time[4]
            second = self.start_date_and_time[5]
            millisecond = self.start_date_and_time[6]

            base_datetime = datetime.datetime(year, month, day, hour, minute, second, millisecond)
        else:
            base_datetime = datetime.datetime(1900, 1, 1, 0, 0, 0, 0)

        number_of_increments = len(self.demand_array)

        timedelta_dict = {
            'microseconds': (1.0 / 3600000000),
            'milliseconds': (1.0 / 3600000),
            'seconds': (1.0 / 3600),
            'minutes': (1.0 / 60),
            'hours': 1,
            'days': 24,
            'weeks': 168
        }

        # calculate end_datetime
        time_increment = timedelta(hours=timedelta_dict[self.time_unit] * self.time_interval)

        datetime_series = [base_datetime + x * time_increment for x in np.arange(0, number_of_increments)]

        demand_timeseries_df = pd.DataFrame({'datetime': datetime_series, 'demand_array': self.demand_array}).set_index('datetime')

        return demand_timeseries_df

    def series_resample(self, new_time_unit, new_time_interval):

        demand_timeseries_df = self.create_datetime_series()

        resample_option_dict = {
            'microseconds': 'us',
            'milliseconds': 'ms',
            'seconds': 'S',
            'minutes': 'min',
            'hours': 'H',
            'days': 'D',
            'weeks': 'W'
        }
        rule_string = str(new_time_interval) + resample_option_dict[new_time_unit]
        resampled_demand_timeseries_df = demand_timeseries_df.resample(rule=rule_string).mean().ffill()
        self.demand_array = resampled_demand_timeseries_df['demand_array']
        self.time_unit = new_time_unit
        self.time_interval = new_time_interval

    def superpose_single(self, other_demand_series, time_unit=None, time_interval=None, test_plot=False):

        same_unit = (self.time_unit == time_unit)
        same_interval = (self.time_interval == time_interval)

        # if resample specified
        if any([time_unit, time_interval]):
            if not time_unit:
                time_unit = self.time_unit
            if not time_interval:
                time_interval = self.time_interval
            for series in [self, other_demand_series]:
                series.series_resample(new_time_unit=time_unit, new_time_interval=time_interval)
        # if resample not specified but samples not same
        # default to self sample properties
        elif False in [same_unit, same_interval]:
            time_unit = self.time_unit
            time_interval = self.time_interval
            other_demand_series.series_resample(new_time_unit=time_unit, new_time_interval=time_interval)
        else:
            time_unit = self.time_unit
            time_interval = self.time_interval

        self_datetime_series_df = self.create_datetime_series()
        other_datetime_series_df = other_demand_series.create_datetime_series()
        print self_datetime_series_df
        # check if gap between series
        self_start = self_datetime_series_df.first_valid_index()
        other_start = other_datetime_series_df.first_valid_index()
        self_finish = self_datetime_series_df.last_valid_index()
        other_finish = other_datetime_series_df.last_valid_index()

        # if gap, define start and length
        gap = False
        if ((self_finish - other_start).total_seconds() < 0):
            gap = True
            series_gap = other_start - self_finish
            series_gap_start = self_finish
        elif ((other_finish - self_start).total_seconds() < 0):
            gap = True
            series_gap = self_start - other_finish
            series_gap_start = other_finish

        # if gap exists, create a time series dataframe for it
        if gap:
            timedelta_dict = {
                'microseconds': (1000000.0),
                'milliseconds': (1000.0),
                'seconds': (1.0),
                'minutes': (1.0 / 60),
                'hours': (1.0 / 3600),
                'days': (1.0 / 86400),
                'weeks': (1.0 / 604800)
            }
            gap_number_of_intervals = series_gap.total_seconds() * timedelta_dict[time_unit] / time_interval
            gap_demand_array = [0] * int(gap_number_of_intervals)
            gap_series = PowerDemandTimeSeries(
                demand_array=gap_demand_array,
                power_unit=self.power_unit,
                time_unit=time_unit,
                time_interval=time_interval,
                start_datetime=series_gap_start
            )

            gap_series_df = gap_series.create_datetime_series()

        concatenated_series_df = pd.concat([self_datetime_series_df, other_datetime_series_df, gap_series_df], axis=1)
        concatenated_series_clean_df = concatenated_series_df.fillna(0)

        if test_plot == True:
            concatenated_series_clean_df.plot()
            plt.show()

        superposed_series_df = concatenated_series_clean_df.groupby(concatenated_series_clean_df.columns, axis=1).sum()
        print superposed_series_df
        superposed_series = PowerDemandTimeSeries(
            demand_array=superposed_series_df['demand_array'],
            power_unit=self.power_unit,
            time_unit=time_unit,
            time_interval=time_interval
        )

        return superposed_series

    def superpose(self, other_demand_series, time_unit=None, time_interval=None, test_plot=False):

        superposed_series = self

        for series in other_demand_series:
            superposed_series = superposed_series.superpose_single(other_demand_series=series, time_unit=time_unit, time_interval=time_interval, test_plot=test_plot)

        return superposed_series

    def plot_demand_series(self):
        demand_series_df = self.create_datetime_series()
        demand_series_df.plot()

    def peak_demand(self):
        peak_demand = np.nanmax(self.demand_array)
        return peak_demand

    def base_demand(self):
        base_demand = np.nanmin(self.demand_array)
        return base_demand

    def total_energy_demand(self, energy_units):

        # total_energy = np.nansum(self.demand_array)
        if energy_units not in ['J', 'MJ', 'GJ', 'TJ', 'Wh', 'kWh', 'MWh', 'GWh', 'TWh']:
            raise ValueError('energy_units must be set as either "J", "MJ", "GJ", "TJ", Wh","kWh","MWh","GWh" or "TWh"')

        day = (1.0 / 24)
        week = (1.0 / 168)
        time_unit_dict_factors = {
            'microseconds': 3600000000.0,
            'milliseconds': 3600000.0,
            'seconds': 3600.0,
            'minutes': 60.0,
            'hours': 1.0,
            'days': day,
            'weeks': week
        }

        energy_unit_factors_dict = {
            'J': 0,
            'MJ': 0,
            'GJ': 0,
            'TJ': 0,
            'Wh': 1,
            'kWh': 0.001,
            'MWh': 0.000001,
            'GWh': 0.000000001,
            'TWh': 0.000000000001
        }

        power_unit_factors_dict = {
            'W': 1,
            'kW': 0.001,
            'MW': 0.000001,
            'GW': 0.000000001,
            'TW': 0.000000000001
        }

        total_energy_base_units = np.nansum(self.demand_array) * self.time_interval

        energy_change_ratio = power_unit_factors_dict[self.power_unit] / energy_unit_factors_dict[energy_units]
        time_change_ratio = 1 / time_unit_dict_factors[self.time_unit]

        total_energy_new_units = total_energy_base_units * time_change_ratio * energy_change_ratio

        return total_energy_new_units

    def change_power_unit(self, new_power_unit):
        """ changes the power unit

        """
        power_unit_factors_dict = {
            'W': 1,
            'kW': 0.001,
            'MW': 0.000001,
            'GW': 0.000000001,
            'TW': 0.000000000001
        }

        if new_power_unit not in power_unit_factors_dict:
            raise ValueError('new_power_unit must be set as either "W","kW","MW","GW" or "TW"')

        demand_in_old_units = self.demand_array
        self.demand_array = power_unit_factors_dict[new_power_unit] * demand_in_old_units / power_unit_factors_dict[self.power_unit]
        self.power_unit = new_power_unit

    def create_load_duration_curve(self, as_percent=True, as_proportion=True, granularity=100):
        '''takes hourly demand data for a period
        returns a two np.arrays, one is list of demand levels
        other is list of time duration spent above those demand levels
        '''

        peak_demand = self.peak_demand()

        # create bins to sort data points
        demand_levels = np.arange(0, self.peak_demand(), (peak_demand / granularity))

        # count data points above each bin and create list noting that count
        # list is the LDC

        duration_above_demand_level_list = list()
        demand_levels_array = self.demand_array
        running_total = 0
        for demand_level in reversed(demand_levels):
            count_above_demand_level = sum(demand_levels_array >= demand_level) + running_total
            running_total = count_above_demand_level
            demand_levels_array = demand_levels_array[demand_levels_array <= demand_level]

            if as_proportion:
                proportion_above_demand_level = count_above_demand_level / float(len(self.demand_array))
                duration_above_demand_level_list.insert(0, proportion_above_demand_level)
            else:
                duration_above_demand_level_list.insert(0, count_above_demand_level)

        duration_above_demand_level_plot = np.append(np.array(duration_above_demand_level_list), 0)
        demand_levels_plot = np.append(demand_levels, peak_demand)

        if as_percent:
            curve_data = [duration_above_demand_level_plot, 100 * demand_levels_plot / peak_demand]

        else:
            curve_data = [duration_above_demand_level_plot, demand_levels_plot]
        load_duration_curve = LoadDurationCurve(
            curve_data=curve_data,
            as_percent=as_percent,
            peak_demand=peak_demand,
            as_proportion=as_proportion,
            granularity=granularity
        )
        return load_duration_curve
