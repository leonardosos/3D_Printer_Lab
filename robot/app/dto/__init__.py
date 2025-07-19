"""
Package containing Data Transfer Objects (DTOs) for the Robot microservice.
"""
from .coordinate_dto import CoordinateDTO
from .progress_dto import ProgressDTO, RobotAction, ActionStatus

__all__ = [
    'CoordinateDTO',
    'ProgressDTO',
    'RobotAction',
    'ActionStatus'
]
