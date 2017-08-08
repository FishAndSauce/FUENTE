import numpy as np


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


def find_lowest_cost_envelope(generator_cost_curve_dict):
    # find lowest y at x = 1 and lowest y at x = 0
    mins_at_extents_dict = find_mins_at_extents(generator_cost_curve_dict=generator_cost_curve_dict)

    # starting at line with lowest x = 1
    # calculate all intersects on line under examination and determine next line in envelope
    current_line = mins_at_extents_dict['one']
    current_position = 1
    
    # instigate generator rank and position lists at x = 1
    generator_rank_list = list()
    x_positions_list = list()
    generator_rank_list.append(current_line)
    x_positions_list.append(1)

    remaining_generator_cost_curve_dict = generator_cost_curve_dict
    while True:
        
        current_line_equation = generator_cost_curve_dict[current_line]
        del remaining_generator_cost_curve_dict[current_line]

        intercepts_on_line_dict = find_intercepts_on_line(
            current_line_equation=current_line_equation,
            other_lines=remaining_generator_cost_curve_dict
            )
        
        for intersept in intercepts_on_line_dict:
            if intercepts_on_line_dict[intersept] > current_position:
                intercepts_on_line_dict[intersept] = None

        current_line = max(
            intercepts_on_line_dict,
            key=intercepts_on_line_dict.get
            )
        current_position = intercepts_on_line_dict[current_line]

        generator_rank_list.append(current_line)
        x_positions_list.append(intercepts_on_line_dict[current_line])

        if current_line == mins_at_extents_dict['zero']:
            break

    lowest_cost_envelope_dict = {'generator_rank_list': generator_rank_list, 'x_positions_list': x_positions_list}
    # retur dict with rank list and corresponding x_positions list
    # where index indicates rank 
    # {'generator_rank_list': ['bio','OCGT',etc], 
    #   'x_positions_list': [1, 0.8, 0.5, 0.3]}
    return lowest_cost_envelope_dict # dict with rank list and corresponding value list{'rank_list': ['bio']}


def find_mins_at_extents(generator_cost_curve_dict):
    cost_at_1_dict = dict()
    cost_at_0_dict = dict()
    mins_at_extents_dict = dict()

    for generator in generator_cost_curve_dict:
        y_at_x_equals_1 = find_y_at_x(
            gradient=generator_cost_curve_dict[generator]['gradient'],
            y_intercept=generator_cost_curve_dict[generator]['y_intercept'],
            x_value=1
            )
        cost_at_1_dict[generator] = y_at_x_equals_1
        y_at_x_equals_0 = find_y_at_x(
            gradient=generator_cost_curve_dict[generator]['gradient'],
            y_intercept=generator_cost_curve_dict[generator]['y_intercept'],
            x_value=0
            )
        cost_at_0_dict[generator] = y_at_x_equals_0
    
    mins_at_extents_dict['zero'] = min(
        cost_at_0_dict,
        key=cost_at_0_dict.get)
    mins_at_extents_dict['one'] = min(
        cost_at_1_dict,
        key=cost_at_1_dict.get)
    return mins_at_extents_dict

def find_y_at_x(gradient, y_intercept, x_value):
    y_value = x_value*gradient + y_intercept
    return y_value

def find_intercepts_on_line(current_line_equation, other_lines):
    intercepts_on_line_dict = dict()
    for line in other_lines:
        m1 = current_line_equation['gradient']
        m2 = other_lines[line]['gradient']
        b1 = current_line_equation['y_intercept']
        b2 = other_lines[line]['y_intercept']
        x = (b1-b2)/(m2-m1)
        intercepts_on_line_dict[line] = x
    return intercepts_on_line_dict


