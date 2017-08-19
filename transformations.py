from classes import StraightLine
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


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


def plot_cost_curves(generator_cost_curve_dict, generator_rank_list=None):

    for generator in generator_cost_curve_dict:
        plot_this = [generator_cost_curve_dict[generator].find_y_at_x(0), generator_cost_curve_dict[generator].find_y_at_x(1)]
        if generator_rank_list:
            plt.plot([0, 1], plot_this, color='gray')
        else:
            plt.plot([0, 1], plot_this, label=generator)

    if generator_rank_list:
        last_index = len(generator_rank_list) - 1
        for i, envelope_generator in enumerate(generator_rank_list):
            label = envelope_generator[0] + ', running @ ' + str(100 * round(envelope_generator[1], 4)) + '% of the year'
            if i != last_index:
                x_values = [generator_rank_list[i + 1][1], envelope_generator[1]]
            else:
                x_values = [0, envelope_generator[1]]
            y_values = [generator_cost_curve_dict[envelope_generator[0]].find_y_at_x(x_values[0]), generator_cost_curve_dict[envelope_generator[0]].find_y_at_x(x_values[1])]
            plt.plot(x_values, y_values, linewidth=2, label=label)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.legend(loc='best', fontsize=10)
    plt.grid()
    plt.show()


def calculate_generation_per_year(load_duration_curve, generator_rank_list):

    area_dict = dict()
    last_index = len(generator_rank_list) - 1
    for i, generator in enumerate(generator_rank_list):
        if i != last_index:
            x_values = [generator_rank_list[i + 1][1], generator[1]]
        else:
            x_values = [0, generator[1]]
        print x_values
        area = load_duration_curve.calculate_ldc_section_area(x_values)
        area_dict[generator[0]] = area
    return area_dict


def plot_ldc_areas(load_duration_curve, generation_per_year_dict, generator_rank_list, required_capacities_dict):

    color_list = ['#808000', '#FFFF00', '#FF0000', '#0000FF', '#FFFF00', '#00FF00', '#00FFFF', '#008080', '#000080', '#FF00FF', '#800080', '#800000']

    # determine x and y values
    curve_list = list()
    curve_list.append([0, 0])
    sum_y_values = 0
    x_values = [0, 1]
    for i, generator in enumerate(generator_rank_list):
        sum_y_values += required_capacities_dict[generator[0]]
        y_values = [sum_y_values, sum_y_values]
        curve_list.append(y_values)
    count = 1
    legend_list = [[], []]
    for curve in reversed(curve_list[1:]):
        plt.fill_between(x_values, curve_list[0], curve, color=color_list[count - 1])
        legend_item_rectangle = Rectangle((0, 0), 1, 1, fc=color_list[count - 1])
        legend_item_text = generator_rank_list[(0 - count)][0] + ': ' + ' @ ' + str(round(required_capacities_dict[generator_rank_list[(0 - count)][0]], 2)) + 'MW & ' + str(100 * round(generator_rank_list[(0 - count)][1], 4)) + '% of the year'
        legend_list[0].append(legend_item_rectangle)
        legend_list[1].append(legend_item_text)
        count += 1
    plt.legend(legend_list[0], legend_list[1], fontsize=10)

    fill_above_ldc_array = np.array([1.01 * sum_y_values] * load_duration_curve.granularity)

    plt.fill_between(load_duration_curve.curve_data[0], load_duration_curve.curve_data[1], fill_above_ldc_array, color='white')

    plt.show()
