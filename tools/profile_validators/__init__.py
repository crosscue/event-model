# Licensed under the Apache License, Version 2.0.

from .mobility import PROFILE_ID as MOBILITY_PROFILE_ID, validate as validate_mobility
from .network import PROFILE_ID as NETWORK_PROFILE_ID, validate as validate_network

VALIDATORS = {
    MOBILITY_PROFILE_ID: validate_mobility,
    NETWORK_PROFILE_ID: validate_network,
}
