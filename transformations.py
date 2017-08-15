from classes import StraightLine, PowerDemandTimeSeries
from operator import attrgetter
import copy
import matplotlib.pyplot as plt


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


def plot_cost_curves(generator_rank_list, generator_cost_curve_dict):

    line_plot = [name[0] for name in generator_rank_list]
    label_here = list()

    for line in line_plot:
        plot_this = [generator_cost_curve_dict[line].find_y_at_x(0), generator_cost_curve_dict[line].find_y_at_x(1)]
        label_here.append((1, plot_this[1]))
        plt.plot(plot_this, '-r')

    for label, xy in zip(line_plot, label_here):
        plt.annotate(
            label,
            xy=xy
        )
    plt.show()
