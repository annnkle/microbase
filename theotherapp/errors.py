class AppError(Exception):
    pass

class WrongFileFormatError(AppError):
    pass

class WrongFileNumberError(AppError):
    pass

class InvalidMetadataError(AppError):
    pass


class InvalidTaxaFileError(AppError):
    DEFAULT_MSG = "Taxa file in invalid format."

    def __init__(self, message=None):
        if not message:
            message = self.DEFAULT_MSG
        super().__init__(message)


class SampleAlreadyUploadedError(AppError):
    pass
