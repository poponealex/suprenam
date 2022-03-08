class UnsupportedOSError(Exception):
    pass


class UnknownInodeError(ValueError):
    """
    The edited text contains an inode absent from the source text.
    """


class TabulationError(ValueError):
    """
    A new name contains a tabulation. Although such a character is valid on most
    platforms, in the edited text it probably results from a typo.
    """


class ValidationError(ValueError):
    """
    A new name includes invalid character(s) for a filename
    (depends on the target platform).
    """


class SeveralTargetsError(Exception):
    """
    Two distinct renaming targets are specified for the same source.
    """


class SeveralSourcesError(Exception):
    """
    Two distinct sources have the same renaming target,
    or a renaming target already exists and has no specified renaming.
    """


class DuplicatedClauseError(Exception):
    """
    A clause (source, target) is specified more than once.
    """


class RecoverableRenamingError(Exception):
    """
    Raised after a failed renaming, with the goal of triggering a rollback.
    """

class RetrieveDefaultsError(Exception):
    """
    Raised when the command for retrieving all defaults fail.
    """
