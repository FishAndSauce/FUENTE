from transformations import find_lowest_cost_envelope, plot_cost_curves
from classes import StraightLine, PowerDemandTimeSeries, LoadDurationCurve
import pandas as pd

# link to preprepared data
working_data_store = pd.HDFStore('working_data_store.h5')

# get raw demand data
hourly_demand_dataframe = working_data_store['hourly_demand_dataframe']

# create LDC
demand_profile = PowerDemandTimeSeries(
    hourly_demand_dataframe['hourly_demand'],
    power_unit="MW",
    time_unit="h",
    time_interval=1
)

load_duration_curve = demand_profile.create_load_duration_curve(as_percent=False, as_proportion=True, granularity=1000)
print load_duration_curve
plt.plot(load_duration_curve[0], load_duration_curve[1])
axis_lims = [0, load_duration_curve[0].max(), 0, (1.01 * load_duration_curve[1].max())]

plt.axis(axis_lims)
plt.show()


# get user inputs and generator characteristics
generators_included_characteristics_dataframe = working_data_store['generators_included_characteristics_dataframe']
# user_inputs_dataframe = working_data_store['user_inputs_dataframe']

generators_included_list = [x.encode('utf-8') for x in generators_included_characteristics_dataframe.index.tolist()]

generator_cost_curve_dict = dict()
for generator in generators_included_list:
    generator_cost_curve_dict[generator] = StraightLine(
        gradient=generators_included_characteristics_dataframe.loc[generator, 'total_variable_cost'],
        y_intercept=generators_included_characteristics_dataframe.loc[generator, 'total_fixed_cost']
        )

# caclulate ranking of generators which forms lowest cost envelope
generator_rank_list= find_lowest_cost_envelope(generator_cost_curve_dict)
print generator_rank_list

load_duration_curve.calculate_ldc_areas(generator_rank_list)

# plot_cost_curves(generator_rank_list, generator_cost_curve_dict)



