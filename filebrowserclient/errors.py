class FileBrowserException(Exception):
    pass


class Forbidden(FileBrowserException):
    pass


class NotFound(FileBrowserException):
    pass


class AuthenticationError(FileBrowserException):
    pass
