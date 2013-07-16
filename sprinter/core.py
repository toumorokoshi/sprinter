"""
Contains core dependencies
"""
import logging
from sprinter.structures import enum

LOGGER = logging.getLogger('sprinter')
PHASES = enum('INSTALL',
              'UPDATE',
              'REMOVE',
              'ACTIVATE',
              'DEACTIVATE',
              'RECONFIGURE',
              'VALIDATE')
