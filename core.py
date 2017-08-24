from transformations import find_lowest_cost_envelope, plot_cost_curves, calculate_generation_per_year, plot_ldc_areas
from classes import StraightLine, PowerDemandTimeSeries
import pandas as pd
import time


# link to preprepared data
working_data_store = pd.HDFStore('working_data_store.h5')

hourly_demand_dataframe = working_data_store['hourly_demand_dataframe']

generators_included_characteristics_dataframe = working_data_store['generators_included_characteristics_dataframe']
hourly_demand_dataframe = working_data_store['hourly_demand_dataframe']

working_data_store.close()

generators_included_list = [x.encode('utf-8') for x in generators_included_characteristics_dataframe.index.tolist()]

start = time.clock()
generator_cost_curve_dict = dict()
for generator in generators_included_list:
    generator_cost_curve_dict[generator] = StraightLine(
        gradient=generators_included_characteristics_dataframe.loc[generator, 'total_variable_cost'],
        y_intercept=generators_included_characteristics_dataframe.loc[generator, 'total_fixed_cost']
    )
print 'generator_cost_curve_dict ', time.clock() - start

start = time.clock()
generator_rank_list = find_lowest_cost_envelope(generator_cost_curve_dict)
print 'find_lowest_cost_envelope ', time.clock() - start

start = time.clock()
demand_profile = PowerDemandTimeSeries(
    hourly_demand_dataframe['hourly_demand'],
    power_unit="MW",
    time_unit="hours",
    time_interval=1
)
print 'PowerDemandTimeSeries ', time.clock() - start

start = time.clock()
load_duration_curve = demand_profile.create_load_duration_curve(as_percent=False, as_proportion=True, granularity=1000)
print 'create_load_duration_curve ', time.clock() - start

start = time.clock()
required_capacities_dict = load_duration_curve.required_capacities(generator_rank_list)
print 'required_capacities ', time.clock() - start


plot_cost_curves(generator_cost_curve_dict=generator_cost_curve_dict)
plot_cost_curves(generator_cost_curve_dict=generator_cost_curve_dict, generator_rank_list=generator_rank_list)

start = time.clock()
generation_per_year_dict = calculate_generation_per_year(load_duration_curve=load_duration_curve, generator_rank_list=generator_rank_list)
print 'calculate_generation_per_year ', time.clock() - start

plot_ldc_areas(
    load_duration_curve=load_duration_curve,
    generation_per_year_dict=generation_per_year_dict,
    generator_rank_list=generator_rank_list,
    required_capacities_dict=required_capacities_dict
)
