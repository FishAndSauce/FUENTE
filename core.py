from transformations import find_lowest_cost_envelope, plot_cost_curves, calculate_generation_per_year, plot_ldc_areas, calculate_cost_of_electricity, calculate_lcoe
from geometry_monkey import StraightLine
from power_monkey import PowerTimeSeries
import pandas as pd
import time


# link to preprepared data
working_data_store = pd.HDFStore('working_data_store.h5')

hourly_demand_dataframe = working_data_store['hourly_demand_dataframe']
wind_and_solar_dataframe = working_data_store['wind_and_solar_dataframe']

generators_included_characteristics_dataframe = working_data_store['generators_included_characteristics_dataframe']
hourly_demand_dataframe = working_data_store['hourly_demand_dataframe']

working_data_store.close()

generators_included_list = [x.encode('utf-8') for x in generators_included_characteristics_dataframe.index.tolist()]

start = time.clock()
generator_cost_curve_dict = dict()
generator_fuel_cost_dict = dict()
carbon_emissions_cost_dict = dict()
vom_cost_dict = dict()
fom_cost_dict = dict()
annualised_capital_dict = dict()

for generator in generators_included_list:
    generator_cost_curve_dict[generator] = StraightLine(
        gradient=generators_included_characteristics_dataframe.loc[generator, 'total_variable_cost'],
        y_intercept=generators_included_characteristics_dataframe.loc[generator, 'total_fixed_cost']
    )
    generator_fuel_cost_dict[generator] = generators_included_characteristics_dataframe.loc[generator, 'total_fuel_cost'] / 8760
    carbon_emissions_cost_dict[generator] = generators_included_characteristics_dataframe.loc[generator, 'total_emissions_cost'] / 8760
    vom_cost_dict[generator] = generators_included_characteristics_dataframe.loc[generator, 'VOM ($/MWh)']
    fom_cost_dict[generator] = generators_included_characteristics_dataframe.loc[generator, 'FOM ($/MW/yr)']
    annualised_capital_dict[generator] = generators_included_characteristics_dataframe.loc[generator, 'Annualised Capital ($/MW/yr)']


print 'generator_cost_curve_dict ', time.clock() - start

start = time.clock()
generator_rank_list = find_lowest_cost_envelope(generator_cost_curve_dict)
print generator_rank_list
print 'find_lowest_cost_envelope ', time.clock() - start

start = time.clock()
demand_profile = PowerTimeSeries(
    demand_array=hourly_demand_dataframe['hourly_demand'],
    power_unit="MW",
    time_unit="hours",
    time_interval=1
)
print 'PowerTimeSeries ', time.clock() - start

solar_profile = PowerTimeSeries(
    demand_array=wind_and_solar_dataframe['solar_output_at_1MW_capacity'] * 2000,
    power_unit="MW",
    time_unit="hours",
    time_interval=1
)

wind_profile = PowerTimeSeries(
    demand_array=wind_and_solar_dataframe['wind_output_at_1MW_capacity'] * 1000,
    power_unit="MW",
    time_unit="hours",
    time_interval=1
)

residual_demand = demand_profile.superpose(other_demand_series=[solar_profile, wind_profile], test_plot=False, time_unit='hours', time_interval=1)

start = time.clock()
load_duration_curve = residual_demand.create_load_duration_curve(as_percent=False, as_proportion=True, granularity=100000)
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

print generator_fuel_cost_dict

total_cost_dict = calculate_cost_of_electricity(generation_per_year_dict, generator_rank_list, required_capacities_dict, carbon_emissions_cost_dict, vom_cost_dict, fom_cost_dict, annualised_capital_dict, generator_fuel_cost_dict)
print 'total_cost_dict ', total_cost_dict
lcoe_dict = calculate_lcoe(total_cost_dict, generation_per_year_dict)
print 'lcoe_dict ', lcoe_dict
