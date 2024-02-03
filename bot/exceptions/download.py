from .base import VoidMusicException


class DownloadError(VoidMusicException):
  def __init__(self, case, error, *args, **kwargs) -> None:
    super().__init__('download', *args)
    self.make_error(case, error, **kwargs)
    