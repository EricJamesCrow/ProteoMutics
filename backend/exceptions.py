class FileNotProcessedError(Exception):
    """Raised when the file hasn't been processed."""
    pass

class PreProcessingError(Exception):
    """Raised during any pre-processing related errors."""
    pass