# -*- coding: utf-8 -*-

# FLEDGE_BEGIN
# See: http://fledge-iot.readthedocs.io/
# FLEDGE_END

""" Module for Sinusoid poll mode plugin """

import copy
import random
import logging

from fledge.common import logger
from fledge.plugins.common import utils

__author__ = "Ashish Jabble"
__copyright__ = "Copyright (c) 2018 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"


_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Sinusoid Poll Plugin which implements sine wave with data points',
        'type': 'string',
        'default': 'sinusoid',
        'readonly': 'true'
    },
    'assetName': {
        'description': 'Name of Asset',
        'type': 'string',
        'default': 'sinusoid',
        'displayName': 'Asset name',
        'mandatory': 'true'
    }
}

_LOGGER = logger.setup(__name__, level=logging.INFO)
index = -1
sine = [
        0.0,
        0.104528463,
        0.207911691,
        0.309016994,
        0.406736643,
        0.5,
        0.587785252,
        0.669130606,
        0.743144825,
        0.809016994,
        0.866025404,
        0.913545458,
        0.951056516,
        0.978147601,
        0.994521895,
        1.0,
        0.994521895,
        0.978147601,
        0.951056516,
        0.913545458,
        0.866025404,
        0.809016994,
        0.743144825,
        0.669130606,
        0.587785252,
        0.5,
        0.406736643,
        0.309016994,
        0.207911691,
        0.104528463,
        1.22515E-16,
        -0.104528463,
        -0.207911691,
        -0.309016994,
        -0.406736643,
        -0.5,
        -0.587785252,
        -0.669130606,
        -0.743144825,
        -0.809016994,
        -0.866025404,
        -0.913545458,
        -0.951056516,
        -0.978147601,
        -0.994521895,
        -1.0,
        -0.994521895,
        -0.978147601,
        -0.951056516,
        -0.913545458,
        -0.866025404,
        -0.809016994,
        -0.743144825,
        -0.669130606,
        -0.587785252,
        -0.5,
        -0.406736643,
        -0.309016994,
        -0.207911691,
        -0.104528463
    ]


def generate_data():
    global index
    while index >= -1:
        # index exceeds, reset to default
        if index >= 59:
            index = -1
        index += 1
        yield sine[index]


def plugin_info():
    """ Returns information about the plugin.
    Args:
    Returns:
        dict: plugin information
    Raises:
    """
    return {
        'name': 'Sinusoid Poll plugin',
        'version': '2.3.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin.
    Args:
        config: JSON configuration document for the South plugin configuration category
    Returns:
        data: JSON object to be used in future calls to the plugin
    Raises:
    """
    data = copy.deepcopy(config)
    return data

# Simulate PLC data
time = 0
SD_interval = 601
SD_duration = 60
LD_interval = 25219
LD_duration = 60
ld_threshold_hold_duration = 0
ld_threshold_exceeded = None

def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.
    Available for poll mode only.
    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        Exception
    """
    global ld_threshold_exceeded, ld_threshold_hold_duration
    global time, SD_interval, SD_duration, LD_interval, LD_duration

    if ld_threshold_hold_duration == 0:
        ld_threshold_hold_duration = random.randint(5*60, 10*60)
        ld_threshold_exceeded = random.randint(0, 1)
        _LOGGER.info("Setting: ld_threshold_hold_duration={}, ld_threshold_exceeded={}".format(ld_threshold_hold_duration, ld_threshold_exceeded))

    try:
        if time>LD_duration and time % LD_interval >= 0 and time % LD_interval <= LD_duration:
            ld=1
        else:
            ld=0
            
        if time>SD_duration and ld==0 and time % SD_interval >= 0 and time % SD_interval <= SD_duration:
            sd=1
        else:
            sd=0

        production = 1-ld
        if not production:
            ld_threshold_exceeded = 0

        ld_threshold_hold_duration = ld_threshold_hold_duration - 1
        plc_data = {"SmallDischarge" : sd, "LargeDischarge" : ld, "Production" : production, "LdThresholdExceeded": ld_threshold_exceeded}

        time_stamp = utils.local_timestamp()
        data = {'asset':  handle['assetName']['value'], 'timestamp': time_stamp, 'readings': plc_data}
        if sd==1 or ld==1 or time%50==0:
            _LOGGER.warn("PLC sim: time={}: {}".format(time, data))
        time += 1
    except (Exception, RuntimeError) as ex:
        _LOGGER.exception("Sinusoid exception: {}".format(str(ex)))
        raise ex
    else:
        return data


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    """
    _LOGGER.info("Old config for sinusoid plugin {} \n new config {}".format(handle, new_config))
    new_handle = copy.deepcopy(new_config)
    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the South plugin service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        plugin shutdown
    """
    _LOGGER.info('sinusoid plugin shut down.')

