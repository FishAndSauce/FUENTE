from transformations import generate_load_duration_curve, find_lowest_cost_envelope
import pandas as pd
import os
import numpy as np

# link to preprepared data
working_data_store = pd.HDFStore('working_data_store.h5')

# get raw demand data
hourly_demand_dataframe = working_data_store['hourly_demand_dataframe']

# get user inputs and generator characteristics
generators_included_characteristics_dataframe = working_data_store['generators_included_characteristics_dataframe']
user_inputs_dataframe = working_data_store['user_inputs_dataframe']
user_inputs_dict = user_inputs_dataframe.to_dict()

# create LDC
hourly_demand_mw_list = hourly_demand_dataframe['hourly_demand']
load_duration_curve_list = generate_load_duration_curve(
    hourly_demand_mw_list=hourly_demand_mw_list)

# determine cost curve line equations
# y = mx+b where m = variable cost and b = fixed cost

# get carbon price and get fuel prices in $/MWh
carbon_price_per_kg = user_inputs_dict['Value']['Carbon Price ($/Tonne)'] / 1000
gas_price_per_mwh = 3.6 * user_inputs_dict['Value']['Gas price ($/GJ)']
coal_price_per_mwh = 3.6 * user_inputs_dict['Value']['Coal price ($/GJ)']
biomass_fuel_price_per_mwh = user_inputs_dict['Value']['Biomass Fuel Price ($/MWh)']

# calculate total fuel cost ($/MW/yr) accounting for thermal efficiency of plant
generators_included_characteristics_dataframe['total_fuel_cost'] = (365 * 24 * 
    (generators_included_characteristics_dataframe['gas_price_cost']
    + generators_included_characteristics_dataframe['coal_price_cost']
    + generators_included_characteristics_dataframe['biomass_price_cost'])
    / generators_included_characteristics_dataframe['Thermal Efficiency'])

# calculate total emmissions cost (KgCO2e/MW/yr)
generators_included_characteristics_dataframe['total_emissions_cost'] = (
    24 * 365 * generators_included_characteristics_dataframe['Carbon Emissions (KgCO2e/MWh)']
    * carbon_price_per_kg)

# calculate total variable cost
generators_included_characteristics_dataframe['total_variable_cost'] = (generators_included_characteristics_dataframe['VOM/year ($/MW/yr)']
    + generators_included_characteristics_dataframe['total_emissions_cost']
    + generators_included_characteristics_dataframe['total_fuel_cost'])
# calculate total fixed cost
generators_included_characteristics_dataframe['total_fixed_cost'] = (generators_included_characteristics_dataframe['Annualised Capital ($/MW/yr)']
    + generators_included_characteristics_dataframe['FOM ($/MW/yr)'])

generator_cost_curve_dict = dict()
for generator in generators_included_list:
    generator_cost_curve_dict[generator] = {'gradient': generators_included_characteristics_dataframe.loc[generator, 'total_variable_cost'], 'y_intercept': generators_included_characteristics_dataframe.loc[generator, 'total_fixed_cost']}

# caclulate lowest envelope
lowest_cost_envelope_dict = find_lowest_cost_envelope(generator_cost_curve_dict)
print lowest_cost_envelope_dict
### LDC and capacity
# intersection of CF and LDC
# calculation of areas under LDC
# calculation of tot cost and emissions

###
# dump outputs
# pretty graphs of outputs
