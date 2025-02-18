from .aadhaar import AadhaarFrontProcessor, AadhaarBackProcessor
from .pan import PANProcessor
from .form16 import Form16Processor
from .base import DocumentProcessor

__all__ = ['AadhaarFrontProcessor', 'AadhaarBackProcessor', 'PANProcessor', 'Form16Processor', 'DocumentProcessor']