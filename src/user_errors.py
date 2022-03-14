class UnsupportedOSError(Exception):
    pass


class NoEditorError(Exception):
    pass


class NoEditorCommandsFileError(Exception):
    pass


class UninstalledFavoriteEditorError(Exception):
    pass


class NoItemToRenameError(Exception):
    """
    A single text file was passed as an argument, and it is empty.
    """


class UnknownInodeError(ValueError):
    """
    The edited text contains an inode absent from the source text.
    """


class TabulationError(ValueError):
    """
    A new name contains a tabulation. Although such a character is valid on most
    platforms, in the edited text it probably results from a typo.
    """


class EmptyNameError(ValueError):
    """
    A new name is empty.
    """


class ValidationError(ValueError):
    """
    A new name is invalid (depends on the target platform).
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
