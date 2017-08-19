from classes import StraightLine, PowerDemandTimeSeries, LoadDurationCurve
import pandas as pd
import matplotlib.pyplot as plt

# import time
# start = time.clock()
# #your code here


# # link to preprepared data
# working_data_store = pd.HDFStore('working_data_store.h5')

# # get raw demand data
# hourly_demand_dataframe = working_data_store['hourly_demand_dataframe']

# working_data_store.close()

# print 'data_gather = ', time.clock() - start

# start = time.clock()

# demand_profile = PowerDemandTimeSeries(
#     hourly_demand_dataframe['hourly_demand'],
#     power_unit="MW",
#     time_unit="h",
#     time_interval=1
# )
# print 'demand_time_series = ', time.clock() - start

# start = time.clock()

# demand_profile.change_power_unit('TW')

# print 'change_units = ', time.clock() - start

# start = time.clock()

# load_duration_curve = demand_profile.create_load_duration_curve(
#     as_percent=False,
#     as_proportion=False,
#     granularity=1000
#     )

# print 'ldc = ', time.clock() - start

# plt.plot(load_duration_curve.curve_data[0], load_duration_curve.curve_data[1])

# plt.show()


# axis_lims = [0, load_duration_curve[0].max(), 0, (1.01 * load_duration_curve[1].max())]


my_line1 = StraightLine(gradient=10, y_intercept=5, x_range=[-2, 2])
my_line2 = StraightLine(gradient=3, y_intercept=-6)
my_line3 = StraightLine(gradient=2.5, y_intercept=-20)

my_line_dict = {'my_line1': my_line1, 'my_line2': my_line2, 'my_line3': my_line3}

intercepts_of_all = my_line1.find_intercepts_on_line(my_line_dict)

x_range = [-4, 4]

for line in my_line_dict.values():
    if line.x_range:
        x_values = [line.x_range[0], line.x_range[1]]
        y_values = [line.find_y_at_x(x_values[0]), line.find_y_at_x(x_values[1])]
        print y_values, x_values
        plt.plot(x_values, y_values)
    else:
        x_values = x_range
        y_values = [line.find_y_at_x(x_values[0]), line.find_y_at_x(x_values[1])]

        plt.plot(x_values, y_values)

plt.show()
