"""
Contains core dependencies
"""
import logging
from sprinter.structures import Enum, EnumInstance

LOGGER = logging.getLogger('sprinter')

PHASE = Enum(
    INSTALL=EnumInstance(name='install', verb='installing'),
    UPDATE=EnumInstance(name='update', verb='updating'),
    REMOVE=EnumInstance(name='remove', verb='removing'),
    ACTIVATE=EnumInstance(name='activate', verb='activating'),
    DEACTIVATE=EnumInstance(name='deactivate', verb='deactivating'),
    RECONFIGURE=EnumInstance(name='reconfigure', verb='reconfiguring'),
    VALIDATE=EnumInstance(name='validate', verb='validating')
)
