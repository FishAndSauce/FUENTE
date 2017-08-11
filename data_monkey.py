import pandas as pd
import os
import numpy as np

# create preproced data storage  
working_data_store = pd.HDFStore('working_data_store.h5')

# set filepath chunks
root_path = 'C:/Users/114261/Optimisation Model/'
user_inputs_path = 'user_inputs'
data_path = 'data'
raw_path = 'raw'
countries_paths = ('australia', 'colombia')
year_paths = ('2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016')

# get raw demand data
demand_filepath = 'hourly_demand_data.csv'
hourly_demand_data_path = os.path.join(root_path, data_path, raw_path, countries_paths[0], year_paths[3], demand_filepath)
working_data_store['hourly_demand_dataframe'] = pd.read_csv(hourly_demand_data_path)

# get user inputs and generator characteristics
user_inputs_path = 'user_inputs'
user_inputs_filename = 'user_inputs.xlsx'
path = os.path.join(root_path, user_inputs_path, user_inputs_filename)
generator_characteristics_dataframe = pd.read_excel(path, sheetname='Generator Characteristics')
user_inputs_dataframe = pd.read_excel(path, sheetname='User Inputs', index_col=0)
user_inputs_dict = user_inputs_dataframe.to_dict()


# Get df of included generators and create generator included list
generators_included_characteristics_dataframe = generator_characteristics_dataframe[generator_characteristics_dataframe['Include?'] == 'Yes'].set_index('Generation Technology')


# get carbon price and get fuel prices in $/MWh
carbon_price_per_kg = user_inputs_dict['Value']['Carbon Price ($/Tonne)'] / 1000
gas_price_per_mwh = 3.6 * user_inputs_dict['Value']['Gas price ($/GJ)']
coal_price_per_mwh = 3.6 * user_inputs_dict['Value']['Coal price ($/GJ)']
biomass_fuel_price_per_mwh = user_inputs_dict['Value']['Biomass Fuel Price ($/MWh)']

# assign generator fuel cost per MWh based on user input (non-matching fuel types will be returned as $0/MWh)
generators_included_characteristics_dataframe['gas_price_cost'] = np.where(
    generators_included_characteristics_dataframe['Fuel Type'] == 'Gas', gas_price_per_mwh, 0)
generators_included_characteristics_dataframe['coal_price_cost'] = np.where(
    generators_included_characteristics_dataframe['Fuel Type'] == 'Coal', coal_price_per_mwh, 0)
generators_included_characteristics_dataframe['biomass_price_cost'] = np.where(
    generators_included_characteristics_dataframe['Fuel Type'] == 'Biomass', biomass_fuel_price_per_mwh, 0)

# calculate total fuel cost ($/MW/yr) accounting for thermal efficiency of plant
generators_included_characteristics_dataframe['total_fuel_cost'] = (365 * 24 * (generators_included_characteristics_dataframe['gas_price_cost']
    + generators_included_characteristics_dataframe['coal_price_cost']
    + generators_included_characteristics_dataframe['biomass_price_cost'])
    /generators_included_characteristics_dataframe['Thermal Efficiency'])

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

working_data_store['generators_included_characteristics_dataframe'] = generators_included_characteristics_dataframe