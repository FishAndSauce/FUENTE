import pandas as pd
import os


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
user_inputs_filename = 'user_inputs.xlsx'
path = os.path.join(root_path, user_inputs_path, user_inputs_filename)
generator_characteristics_dataframe = pd.read_excel(path, sheetname='Generator Characteristics')

# Get df of included generators and create generator included list
generators_included_characteristics_dataframe = generator_characteristics_dataframe[generator_characteristics_dataframe['Include?'] == 'Yes'].set_index('Generation Technology')
generators_included_list = [x.encode('utf-8') for x in generators_included_characteristics_dataframe.index.tolist()]
# assign generator fuel cost per MWh based on user input (non-matching fuel types will be returned as $0/MWh)
generators_included_characteristics_dataframe['gas_price_cost'] = np.where(
    generators_included_characteristics_dataframe['Fuel Type'] == 'Gas', gas_price_per_mwh, 0)
generators_included_characteristics_dataframe['coal_price_cost'] = np.where(
    generators_included_characteristics_dataframe['Fuel Type'] == 'Coal', coal_price_per_mwh, 0)
generators_included_characteristics_dataframe['biomass_price_cost'] = np.where(
    generators_included_characteristics_dataframe['Fuel Type'] == 'Biomass', biomass_fuel_price_per_mwh, 0)


working_data_store['generators_included_characteristics_dataframe'] = generators_included_characteristics_dataframe

working_data_store['user_inputs_dataframe'] = pd.read_excel(path, sheetname='User Inputs', index_col=0)
