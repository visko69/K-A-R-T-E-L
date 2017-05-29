class DownloaderException(Exception):
    """
    Base class for Downloader exceptions.
    """
    pass


class GitException(DownloaderException):
    """
    Generic class for git exceptions.
    """


class InvalidRepoName(DownloaderException):
    """
    Throw when a repo name is invalid. Check
        the message for a more detailed reason.
    """
    pass


class ExistingGitRepo(DownloaderException):
    """
    Thrown when trying to clone into a folder where a
        git repo already exists.
    """
    pass


class MissingGitRepo(DownloaderException):
    """
    Thrown when a git repo is expected to exist but
        does not.
    """
    pass


class CloningError(GitException):
    """
    Thrown when git clone returns a non zero exit code.
    """
    pass


class CurrentHashError(GitException):
    """
    Thrown when git returns a non zero exit code attempting
        to determine the current commit hash.
    """
    pass
