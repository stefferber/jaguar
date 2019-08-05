# -*- coding: utf-8 -*-
"""Charge logging script

This script will download the get_vehicle_status every 5 minutes
and log them locally. Based on the Charge Off-Peak script.


"""

import jlrpy
import threading
import datetime
import math

from datetime import date
import os
import configparser


# login info (email and password) are read from $HOME/.jlrpy.cfg
# which contains a single line with email and password separated by ':'
# email@example.com:PassW0rd
# passwords containing a ':' are not allowed

logger = jlrpy.logger



def check_soc():
    """Retrieve vehicle status.
    """
    threading.Timer(2*60.0, check_soc).start()  # Called every 5 minutes

    # getting status update
    status = { d['key'] : d['value'] for d in v.get_status()['vehicleStatus'] }

    current_soc = int(status['EV_STATE_OF_CHARGE'])
    charging_status = status['EV_CHARGING_STATUS']
    logger.info("current SoC is "+str(current_soc)+"%")

    if status['EV_CHARGING_METHOD']  == "WIRED":
        logger.info("car is plugged in")
        logger.info("charging status is "+charging_status)

        p = v.get_position()
        position = (p['position']['latitude'], p['position']['longitude'])
        logger.info("car geo-position is "+str(position))

        t = datetime.datetime.now()
        clogfilename = "jaguar-logs/charging-log_" + t.strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        clogfile= open(clogfilename,"w+")
        logger.info("writing charging log file " + clogfilename)

        # getting health status forces a status update
        healthstatus = v.get_health_status()
        status = { d['key'] : d['value'] for d in v.get_status()['vehicleStatus']}
        logtime = ", 'LOGTIMESTAMP': '"+ t.isoformat() +"'}"
        clogfile.write(str(status).replace("}", "") + logtime)
        clogfile.close()    
        
    else:
        logger.info("car is not plugged in")

config = configparser.ConfigParser()
configfile = os.environ['HOME']+"/.jlrpy.ini"
config.read(configfile)
username = config['jlrpy']['email']
password = config['jlrpy']['password']
home = (float(config['jlrpy']['home_latitude']), float(config['jlrpy']['home_longitude']))

c = jlrpy.Connection(username, password)
v = c.vehicles[0]

logger.info("[*] Logging vehicle status")
check_soc()
