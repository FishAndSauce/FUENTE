from classes import StraightLine, PowerDemandTimeSeries, LoadDurationCurve
import pandas as pd


working_data_store = pd.HDFStore('working_data_store.h5')


hourly_demand_dataframe = working_data_store['hourly_demand_dataframe']

working_data_store.close()


demand_profile = PowerDemandTimeSeries(
    hourly_demand_dataframe['hourly_demand'],
    power_unit="mW",
    time_unit="h",
    time_interval=1
)

total_energy = demand_profile.total_energy_demand()

ldc = demand_profile.create_load_duration_curve(as_percent=False, as_proportion=True, granularity=1000)
y_value = ldc.locate_y_at_x(x_value=0.5)

area = ldc.calculate_ldc_area(x_values=[0, 1])
print area / total_energy
