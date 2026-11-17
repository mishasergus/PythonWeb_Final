class DefaultError(Exception):
    def __str__(self):
        return "An unexpected error occurred."

class TextEmptyError(DefaultError):
    def __str__(self):
        return "Comment text cannot be empty."

class ApplicationClosedError(DefaultError):
    def __str__(self):
        return "Cannot add comments to a closed application."

class ApplicationRejectedError(DefaultError):
    def __str__(self):
        return "Cannot add comments to a rejected application."

class InvalidStatusTransitionError(DefaultError):
    def __str__(self):
        return "Invalid status transition for this application."