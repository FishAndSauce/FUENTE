import numpy as np
from classes import StraightLine
from operator import attrgetter
import copy


def generate_load_duration_curve(hourly_demand_mw_list):
    # takes hourly demand data for a period
    # returns a list with demand data transformed
    # list is in form of a load duration curve (LDC)

    # get peak demand value
    # transform hourly demand data into percentage of peak demand
    peak_demand_mw = hourly_demand_mw_list.max()
    hourly_demand_as_percent_of_peak = 100 * hourly_demand_mw_list / peak_demand_mw

    # create bins to sort data points
    percent_bins_list = range(0, 100)

    # count data points above each bin and create list noting that count
    # list is the LDC
    load_duration_curve_data_list = list()
    for bin_edge in percent_bins_list:
        count_values_above_bin_edge = sum(hourly_demand_as_percent_of_peak >= bin_edge)
        load_duration_curve_data_list.append(count_values_above_bin_edge)
    return load_duration_curve_data_list


def find_mins_at_extents(generator_cost_curve_dict):
    cost_at_1_dict = dict()
    cost_at_0_dict = dict()
    mins_at_extents_dict = dict()

    for generator in generator_cost_curve_dict:
        y_at_x_equals_1 = generator_cost_curve_dict[generator].find_y_at_x(1)
        cost_at_1_dict[generator] = y_at_x_equals_1
        y_at_x_equals_0 = generator_cost_curve_dict[generator].find_y_at_x(0)
        cost_at_0_dict[generator] = y_at_x_equals_0

    mins_at_extents_dict['zero'] = min(cost_at_0_dict, key=cost_at_0_dict.get)
    mins_at_extents_dict['one'] = min(cost_at_1_dict, key=cost_at_1_dict.get)
    print mins_at_extents_dict['zero']

    return mins_at_extents_dict


def find_lowest_cost_envelope(generator_cost_curve_dict):

    # find lowest y at x = 1 and lowest y at x = 0
    mins_at_extents_dict = find_mins_at_extents(generator_cost_curve_dict=generator_cost_curve_dict)

    # instigate generator rank and position lists at x = 1
    current_line_name = mins_at_extents_dict['one']
    current_position = 1
    generator_rank_list = list()
    generator_rank_list.append((mins_at_extents_dict['one'], 1))

    # create dict from which lines will be removed as they are selected
    # as part of envelope
    remaining_generator_cost_curve_dict = copy.deepcopy(generator_cost_curve_dict)
    while True:

        current_line = generator_cost_curve_dict[current_line_name]
        del remaining_generator_cost_curve_dict[current_line_name]

        intercepts_on_line_dict = current_line.find_intercepts_on_line(
            other_lines=remaining_generator_cost_curve_dict
        )
        # null out unwanted values that do not lie between current position and 0
        for intersept in intercepts_on_line_dict:
            if intercepts_on_line_dict[intersept] > current_position:
                intercepts_on_line_dict[intersept] = None

        # find next line in envelope and set as current line
        current_line_name = max(
            intercepts_on_line_dict,
            key=intercepts_on_line_dict.get
        )

        current_position = intercepts_on_line_dict[current_line_name]
        generator_rank_list.append((current_line_name, intercepts_on_line_dict[current_line_name]))

        if current_line_name == mins_at_extents_dict['zero']:
            break

    return generator_rank_list
