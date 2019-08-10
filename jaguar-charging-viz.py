# -*- coding: utf-8 -*-
"""Charging visualization  script

This script visualizes charging log json files logged by jaguar-charing.py 
in the source directory

This script is independent from logging in order to run it on different computers
 
"""


import threading
import datetime
import math

from datetime import date
import os
import logging
import json
import glob
import configparser
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate



battery_max_energy = 84.7


""" only this subset of vehicle status data will be fetched
"""
data_columns = [
"LOGTIMESTAMP",   
"BATTERY_VOLTAGE",
"EV_BATTERY_PRECONDITIONING_STATUS",
"EV_CHARGE_NOW_SETTING",
"EV_CHARGE_TYPE",
"EV_CHARGING_METHOD",
"EV_CHARGING_MODE_CHOICE",
"EV_CHARGING_RATE_KM_PER_HOUR",
"EV_CHARGING_RATE_MILES_PER_HOUR",
"EV_CHARGING_RATE_SOC_PER_HOUR",
"EV_CHARGING_STATUS", 
"EV_ENERGY_CONSUMED_LAST_CHARGE_KWH",
"EV_IS_CHARGING",
"EV_IS_PLUGGED_IN",
"EV_IS_PRECONDITIONING",
"EV_MINUTES_TO_BULK_CHARGED",
"EV_MINUTES_TO_FULLY_CHARGED",
"EV_ONE_OFF_MAX_SOC_CHARGE_SETTING_CHOICE",
"EV_PERMANENT_MAX_SOC_CHARGE_SETTING_CHOICE",
"EV_PRECONDITIONING_MODE",
"EV_PRECONDITION_FUEL_FIRED_HEATER_SETTING",
"EV_PRECONDITION_OPERATING_STATUS",
"EV_PRECONDITION_PRIORITY_SETTING",
"EV_PRECONDITION_REMAINING_RUNTIME_MINUTES",
"EV_RANGE_COMFORTx10",
"EV_RANGE_ECOx10",
"EV_RANGE_GET_ME_HOMEx10",
"EV_RANGE_ON_BATTERY_KM",
"EV_RANGE_ON_BATTERY_MILES",
"EV_RANGE_PREDICT_STATUS",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD1",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD2",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD3",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD4",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD5",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD6",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD7",
"EV_RANGE_VSC_HV_ENERGY_ASCENTx10",
"EV_RANGE_VSC_HV_ENERGY_DESCENTx10",
"EV_RANGE_VSC_HV_ENERGY_TIME_PENx100",
"EV_RANGE_VSC_INITIAL_HV_BATT_ENERGYx100",
"EV_RANGE_VSC_RANGE_MAP_REFACTR_COMF",
"EV_RANGE_VSC_RANGE_MAP_REFACTR_ECO",
"EV_RANGE_VSC_RANGE_MAP_REFACTR_GMH",
"EV_RANGE_VSC_REGEN_ENERGY_AVAILABLEx100",
"EV_RANGE_VSC_REGEN_ENERGY_FACTOR",
"EV_RANGE_VSC_REVISED_HV_BATT_ENERGYx100",
"EV_RANGE_VSC_VEH_ACCEL_FACTOR",
"EV_STATE_OF_CHARGE",
"ODOMETER_METER",
"TRANSPORT_MODE_START",
"TRANSPORT_MODE_STOP",
"TU_STATUS_SERIAL_NUMBER",
"TU_STATUS_SLEEP_CYCLES_START_TIME",
"POSITION_LATITUDE",
"POSITION_LONGITUDE"]

data_columns_daytime  = [
"LOGTIMESTAMP",
"TU_STATUS_SLEEP_CYCLES_START_TIME",
"TRANSPORT_MODE_START",
"TRANSPORT_MODE_STOP",
"TU_STATUS_SLEEP_CYCLES_START_TIME"]

data_columns_float = [
"BATTERY_VOLTAGE",
"EV_CHARGING_RATE_KM_PER_HOUR",
"EV_CHARGING_RATE_MILES_PER_HOUR",
"EV_CHARGING_RATE_SOC_PER_HOUR",
"EV_ENERGY_CONSUMED_LAST_CHARGE_KWH",
"EV_MINUTES_TO_BULK_CHARGED",
"EV_MINUTES_TO_FULLY_CHARGED",
"EV_PRECONDITION_REMAINING_RUNTIME_MINUTES",
"EV_RANGE_COMFORTx10",
"EV_RANGE_ECOx10",
"EV_RANGE_GET_ME_HOMEx10",
"EV_RANGE_ON_BATTERY_KM",
"EV_RANGE_ON_BATTERY_MILES",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD1",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD2",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD3",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD4",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD5",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD6",
"EV_RANGE_VSC_HV_BATTERY_CONSUMPTION_SPD7",
"EV_RANGE_VSC_HV_ENERGY_ASCENTx10",
"EV_RANGE_VSC_HV_ENERGY_DESCENTx10",
"EV_RANGE_VSC_HV_ENERGY_TIME_PENx100",
"EV_RANGE_VSC_INITIAL_HV_BATT_ENERGYx100",
"EV_RANGE_VSC_RANGE_MAP_REFACTR_COMF",
"EV_RANGE_VSC_RANGE_MAP_REFACTR_ECO",
"EV_RANGE_VSC_RANGE_MAP_REFACTR_GMH",
"EV_RANGE_VSC_REGEN_ENERGY_AVAILABLEx100",
"EV_RANGE_VSC_REGEN_ENERGY_FACTOR",
"EV_RANGE_VSC_REVISED_HV_BATT_ENERGYx100",
"EV_RANGE_VSC_VEH_ACCEL_FACTOR",
"EV_STATE_OF_CHARGE",
"ODOMETER_METER"]


data_columns_print  = [
"LOGTIMESTAMP",
"EV_CHARGING_RATE_KM_PER_HOUR",
"EV_CHARGING_RATE_SOC_PER_HOUR",
"EV_MINUTES_TO_BULK_CHARGED",
"EV_MINUTES_TO_FULLY_CHARGED",
"EV_RANGE_ON_BATTERY_KM",
"EV_STATE_OF_CHARGE",
"ODOMETER_METER",
"POSITION_LATITUDE",
"POSITION_LONGITUDE"]

""" Smallest subset
data_columns = [
"LOGTIMESTAMP",   
"EV_CHARGING_RATE_KM_PER_HOUR",
"EV_CHARGING_RATE_SOC_PER_HOUR",
"EV_RANGE_ON_BATTERY_KM",
"EV_STATE_OF_CHARGE"]
"""

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("jaguar-logs-viz")
logger.info("[*] Logging charging vizualization")


""" Part I: Fetching files from remote directory or remote machine 
    !missing: Required if the computer logging the files is different 
"""

""" Part II: iterating over all files in one folder and organizing them in a sorted time series
    
"""

directory_charging_log = "jaguar-logs"
json_pattern = os.path.join(directory_charging_log,'charging-log*.json')
list_charging_log = glob.glob(json_pattern)
list_charging_log.sort()
data = []
charging_data_row = []

"""!missing: wrong format file detection """
    
for charging_log_file in list_charging_log:
    
    if os.stat(charging_log_file).st_size > 0 :
        clogfile= open(charging_log_file,"r")
        charging_data_row = eval(clogfile.read())
        data_row = []                              
        for item in data_columns:
            if item in charging_data_row :
                data_row.append(charging_data_row[item])
            else :
                data_row.append('NA')
        data.append(data_row)
        clogfile.close()    
    else:
        logger.warning("could not read charging log file " + charging_log_file) 

        

""" Part III: Vizualization of time series
""" 

""" Generate time series with panda
"""
timeseries = pd.DataFrame(data, columns=data_columns)


""" Clean up data and define data types in timeseries
"""
timeseries['EV_CHARGING_RATE_SOC_PER_HOUR'] = timeseries['EV_CHARGING_RATE_SOC_PER_HOUR'].replace('UNKNOWN', '0.0')

for item in data_columns_float:
    timeseries = timeseries.astype({item :'float64'})

for item in data_columns_daytime:
    timeseries[item] = pd.to_datetime(timeseries[item])


""" Printing all data at once needs a lot of space
print(tabulate(timeseries, headers='keys', tablefmt='psql'))
"""

""" Printing only a subset as define in data_columns_print 
"""
print(tabulate(timeseries[data_columns_print], headers='keys', tablefmt='psql'))


""" plot all data points in one graph SoC vs. SoC/h: 
"""
timeseries.plot(kind='scatter',x='EV_STATE_OF_CHARGE',y='EV_CHARGING_RATE_SOC_PER_HOUR',color='red', title='all charging logs')
plt.xlabel('EV_STATE_OF_CHARGE [%]')
plt.ylabel('EV_CHARGING_RATE_SOC_PER_HOUR [%]')
plt.show()

""" plot for each charging process one graph SoC vs. SoC/h
    charging logs are grouped by odometer reading as the most simple heuristic to discriminate charging processes
"""
""" !missing: I don't know how I can put the TIMESTAMP in each graph in order to identify which charging process is in the graph
"""
chargingseries=timeseries.groupby(['ODOMETER_METER'])
for odometerindex, plotindex in chargingseries :    
    plotindex.plot(style='.-',x='EV_STATE_OF_CHARGE',y='EV_CHARGING_RATE_SOC_PER_HOUR',color='black', title='ODOMETER_METER =' + str(odometerindex/1000) + ' km', legend=None)

plt.xlabel('EV_STATE_OF_CHARGE [%]')
plt.ylabel('EV_CHARGING_RATE_SOC_PER_HOUR [%]')
plt.show()

""" plot all data points in one graph: 
"""
timeseries.plot(kind='scatter',x='EV_STATE_OF_CHARGE',y='EV_MINUTES_TO_FULLY_CHARGED',color='blue', title='all charging logs')
plt.xlabel('EV_STATE_OF_CHARGE [%]')
plt.ylabel('EV_MINUTES_TO_FULLY_CHARGED [Min]')
plt.show()

""" plot all data points in one graph date-time vs SoC: 
"""
timeseries.plot(x='LOGTIMESTAMP',y='EV_STATE_OF_CHARGE',color='green', title='all charging logs')
plt.xlabel('LOGTIMESTAMP [date-time]')
plt.ylabel('EV_STATE_OF_CHARGE [%]')
plt.show()


""" plot all data points in one graph: date-time vs. SoC & Energy
"""
ax = plt.gca() # get current axis for multiple line plots
timeseries.plot(x='LOGTIMESTAMP',y='EV_STATE_OF_CHARGE',color='green', ax=ax)
timeseries.plot(x='LOGTIMESTAMP',y='EV_RANGE_VSC_INITIAL_HV_BATT_ENERGYx100',color='blue', ax=ax)
timeseries.plot(x='LOGTIMESTAMP',y='EV_RANGE_VSC_REVISED_HV_BATT_ENERGYx100',color='black', ax=ax)
#timeseries.plot(x='LOGTIMESTAMP',y='EV_ENERGY_CONSUMED_LAST_CHARGE_KWH',color='yellow', ax=ax)
plt.title('Correlation of SoC & Energy in Battery')
plt.xlabel('LOGTIMESTAMP [date-time]')
plt.ylabel('EV_STATE_OF_CHARGE [%] | EV_RANGE_VSC [kW]')

plt.show()


""" Part IV:Correlation analysis of data
    !missing: Complete correlation map for all integer and floats in the timeseries
    like https://medium.com/@sebastiannorena/finding-correlation-between-many-variables-multidimensional-dataset-with-python-5deb3f39ffb3 
"""
print(timeseries['EV_STATE_OF_CHARGE'].corr(timeseries['EV_RANGE_VSC_INITIAL_HV_BATT_ENERGYx100']))
print(timeseries['EV_STATE_OF_CHARGE'].corr(timeseries['EV_RANGE_VSC_REVISED_HV_BATT_ENERGYx100']))
print(timeseries['EV_RANGE_VSC_INITIAL_HV_BATT_ENERGYx100'].corr(timeseries['EV_RANGE_VSC_REVISED_HV_BATT_ENERGYx100']))



