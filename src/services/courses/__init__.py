"""
Services Courses - Exports
"""
from .courses_service import courses_service, MAGASINS_CONFIG
from .courses_ai_service import create_courses_ai_service

__all__ = ["courses_service", "MAGASINS_CONFIG", "create_courses_ai_service"]
