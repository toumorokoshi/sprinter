"""
Contains core dependencies
"""
import logging
from sprinter.structures import enum, EnumInstance

LOGGER = logging.getLogger('sprinter')

PHASES = enum(
    INSTALL=EnumInstance(phase_name='install', verb='installing'),
    UPDATE=EnumInstance(phase_name='update', verb='updating'),
    REMOVE=EnumInstance(phase_name='remove', verb='removing'),
    ACTIVATE=EnumInstance(phase_name='activate', verb='activating'),
    DEACTIVATE=EnumInstance(phase_name='deactivate', verb='deactivating'),
    RECONFIGURE=EnumInstance(phase_name='reconfigure', verb='reconfiguring'),
    VALIDATE=EnumInstance(phase_name='validate', verb='validating')
    )
