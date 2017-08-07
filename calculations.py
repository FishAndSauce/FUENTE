
def generate_load_duration_curve(hourly_demand_mw_list):
    # takes hourly demand data for a period
    # returns a list with demand data transformed
    # list is in form of a load duration curve (LDC)

    # get peak demand value
    # transform hourly demand data into percentage of peak demand

    peak_demand_mw = hourly_demand_mw_list.max()
    hourly_demand_as_percent_of_peak = 100 * hourly_demand_mw_list / peak_demand_mw

    # create bins to sort data points
    percent_bins_list = range(0, 100)

    # count data points above each bin and create list noting that count
    # list is the LDC
    load_duration_curve_data_list = list()
    for bin_edge in percent_bins_list:
        count_values_above_bin_edge = sum(hourly_demand_as_percent_of_peak >= bin_edge)
        load_duration_curve_data_list.append(count_values_above_bin_edge)
    return load_duration_curve_data_list
