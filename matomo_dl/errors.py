class MatomoError(Exception):
    ...


class MissingDownloadError(MatomoError):
    ...


class VersionError(MatomoError):
    ...


class DownloadHashMismatch(MatomoError):
    ...
