from transformations import generate_load_duration_curve, find_lowest_cost_envelope
from classes import StraightLine, PowerDemandTimeSeries
import pandas as pd


# link to preprepared data
working_data_store = pd.HDFStore('working_data_store.h5')

# get raw demand data
hourly_demand_dataframe = working_data_store['hourly_demand_dataframe']

# create LDC
hourly_demand_mw_list = hourly_demand_dataframe['hourly_demand']
load_duration_curve_list = generate_load_duration_curve(
    hourly_demand_mw_list=hourly_demand_mw_list)

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


# LDC and capacity
# intersection of CF and LDC
# calculation of areas under LDC
# calculation of tot cost and emissions

###
# dump outputs
# pretty graphs of outputs
