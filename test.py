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


my_line1 = StraightLine(gradient=10, y_intercept=5)
my_line2 = StraightLine(gradient=3, y_intercept=-6)
my_line3 = StraightLine(gradient=2.5, y_intercept=-200)
y_value = my_line1.find_y_at_x(6)


my_line_dict = {'my_line2': my_line2, 'my_line3': my_line3}

intercept_of_2 = my_line1.find_intercept_on_line(my_line2)
intercept_of_3 = my_line1.find_intercept_on_line(my_line3)
print 'my_line2 = ', intercept_of_2, 'my_line3 = ', intercept_of_3

intercepts_of_all = my_line1.find_intercepts_on_line(my_line_dict)
print intercepts_of_all
