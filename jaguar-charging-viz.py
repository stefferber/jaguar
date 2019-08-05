# -*- coding: utf-8 -*-
"""Charging visualization  script

This script will vizulaizes charging log json files logged by jaguar-charing.py 
in the source directory


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


battery_max_energy = 84.7


""" only this subset of vehicle status data will be fetched
"""
data_columns = [
"LOGTIMESTAMP",   
"BATTERY_VOLTAGE",
"DISTANCE_TO_EMPTY_FUEL",
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
"EV_PHEV_RANGE_COMBINED_KM",
"EV_PHEV_RANGE_COMBINED_MILES",
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
"TU_STATUS_POWER",
"TU_STATUS_PRIMARY_CHARGE_PERCENT",
"TU_STATUS_PRIMARY_VOLT",
"TU_STATUS_SECONDARY_VOLT",
"TU_STATUS_SERIAL_NUMBER",
"TU_STATUS_SLEEP_CYCLES_START_TIME"]

data_columns_daytime  = [
"LOGTIMESTAMP",
"TU_STATUS_SLEEP_CYCLES_START_TIME",
"TRANSPORT_MODE_START",
"TRANSPORT_MODE_STOP",
"TU_STATUS_SLEEP_CYCLES_START_TIME"]

data_columns_float = [
"BATTERY_VOLTAGE",
"DISTANCE_TO_EMPTY_FUEL",
"EV_CHARGING_RATE_KM_PER_HOUR",
"EV_CHARGING_RATE_MILES_PER_HOUR",
"EV_CHARGING_RATE_SOC_PER_HOUR",
"EV_ENERGY_CONSUMED_LAST_CHARGE_KWH",
"EV_MINUTES_TO_BULK_CHARGED",
"EV_MINUTES_TO_FULLY_CHARGED",
"EV_PHEV_RANGE_COMBINED_KM",
"EV_PHEV_RANGE_COMBINED_MILES",
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
"ODOMETER_METER",
"TU_STATUS_PRIMARY_CHARGE_PERCENT",
"TU_STATUS_PRIMARY_VOLT",
"TU_STATUS_SECONDARY_VOLT"]


""" Smallest subset
data_columns = [
"LOGTIMESTAMP",   
"EV_CHARGING_RATE_KM_PER_HOUR",
"EV_CHARGING_RATE_SOC_PER_HOUR",
"EV_RANGE_ON_BATTERY_KM",
"EV_STATE_OF_CHARGE"]
"""



""" Part I: Fetching files from directory or remote machine 
    !missing
"""

""" Part II: iterating over all files in one folder and organizing them in a sorted time series
    
"""


directory_charging_log = "jaguar-logs"
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("jaguar-logs-viz")
logger.info("[*] Logging charging vizualization")

json_pattern = os.path.join(directory_charging_log,'charging-log*.json')
list_charging_log = glob.glob(json_pattern)
list_charging_log.sort()
data = []
charging_data_row = []

"""!missing GPS information"""
"""!missing: wrong format file detection """
    
for charging_log_file in list_charging_log:
    
    if os.stat(charging_log_file).st_size > 0 :
        clogfile= open(charging_log_file,"r")
        charging_data_row = eval(clogfile.read())
        data_row = []                              
        for item in data_columns:
            data_row.append(charging_data_row[item])
            data.append(data_row)
        clogfile.close()    
    else:
        logger.warning("could not read charging log file " + charging_log_file) 

        

""" Part III: Vizualization of time series
""" 

timeseries = pd.DataFrame(data, columns=data_columns)


""" manual conversion
timeseries.apply(pd.to_numeric, errors='ignore')
timeseries['LOGTIMESTAMP'] = pd.to_datetime(timeseries['LOGTIMESTAMP'])
timeseries.EV_CHARGING_RATE_KM_PER_HOUR=timeseries.EV_CHARGING_RATE_KM_PER_HOUR.astype(float)
timeseries['EV_CHARGING_RATE_SOC_PER_HOUR'] = timeseries['EV_CHARGING_RATE_SOC_PER_HOUR'].replace('UNKNOWN', '0.0')
timeseries.EV_CHARGING_RATE_SOC_PER_HOUR=timeseries.EV_CHARGING_RATE_SOC_PER_HOUR.astype(float)
timeseries.EV_RANGE_ON_BATTERY_KM = timeseries.EV_RANGE_ON_BATTERY_KM.astype(float)
timeseries.EV_STATE_OF_CHARGE = timeseries.EV_STATE_OF_CHARGE.astype(float)
timeseries.EV_MINUTES_TO_FULLY_CHARGED = timeseries.EV_MINUTES_TO_FULLY_CHARGED.astype(float)
"""

timeseries['EV_CHARGING_RATE_SOC_PER_HOUR'] = timeseries['EV_CHARGING_RATE_SOC_PER_HOUR'].replace('UNKNOWN', '0.0')

for item in data_columns_float:
    timeseries = timeseries.astype({item :'float64'})

for item in data_columns_daytime:
    timeseries[item] = pd.to_datetime(timeseries[item])


timeseries.plot(kind='scatter',x='EV_STATE_OF_CHARGE',y='EV_CHARGING_RATE_SOC_PER_HOUR',color='red')
plt.show()

"""
timeseries.groupby(['ODOMETER_METER']).plot(kind='line',x='EV_STATE_OF_CHARGE',y='EV_CHARGING_RATE_SOC_PER_HOUR',color='black', title='ODOMETER_METER')
"""
timeseries.groupby(['ODOMETER_METER']).plot(style='.-',x='EV_STATE_OF_CHARGE',y='EV_CHARGING_RATE_SOC_PER_HOUR',color='black', title='ODOMETER_METER')
plt.show()


timeseries.plot(kind='scatter',x='EV_STATE_OF_CHARGE',y='EV_MINUTES_TO_FULLY_CHARGED',color='blue')
plt.show()

timeseries.plot(x='LOGTIMESTAMP',y='EV_STATE_OF_CHARGE',color='green')
plt.show()
