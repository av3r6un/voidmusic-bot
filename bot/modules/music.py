from bot.exceptions import DownloadError
from pytube import YouTube
import ffmpeg
import os


class VoidMusic:
  def __init__(self, link, logger, config):
    self.logger = logger
    self.settings = config
    self.highest_abr = ''
    self.yt = YouTube(link)
    self.yid = self.yt.video_id
    self.title = self.yt.title

  def download(self):
    author = self.yt.author
    song = self.yt.streams.filter(only_audio=True, abr=f'{self._get_highest_abr()}').first()
    self.filename = f'{self._allowed_filename(author)}-{self._allowed_filename(song.title)}'
    if not self._is_worth_downloading():
      raise DownloadError('filesize', 'too_large')
    song.download(filename=f'{self.filename}.wav')
    self.logger.info(f'Downloaded {self.filename} with abr: {self.highest_abr}')
    path = self._convert()
    return path  

  def _get_highest_abr(self):
    br = [br.abr for br in self.yt.streams.filter(only_audio=True)]
    i = max([i for i, br in enumerate(br)])
    self._abr = br[i]
    return br[i]
  
  def _allowed_filename(self, title):
    repl = {' ': '_'} | {k: '' for k in self.settings.BANNED_WORDS}
    return ''.join(repl.get(c, c) for c in title).strip('_')
  
  def _is_worth_downloading(self):
    fs = ((self._abr * self.yt.length) / 8) / 10**6
    if fs < 50:
      return True
    return False
  
  def _convert(self):
    self.latest = f'{self.settings.STORAGE}/{self.filename}.mp3'
    try:
      proc = (
        ffmpeg
        .input(f'{self.settings.STORAGE}/{self.filename}.wav')
        .output(f'{self.settings.STORAGE}/{self.filename}.mp3', **{'c:a': 'libmp3lame'})
        .overwrite_output()
        .global_args('-loglevel', 'quiet')
        .run_async(pipe_stdout=True)
      )
      proc.wait()
      self.logger.info(f'Successfully converted {self.filename} into MP3 format.')
      return f'{self.settings.STORAGE}/{self.filename}.mp3'
    except Exception as ex:
      self.logger.error(f'Conversion into MP3 format failed. Traceback: {str(ex)}')
    finally:
      os.remove(f'{self.settings.STORAGE}{self.filename}.wav')
  
  def delete_latest(self):
    os.remove(self.latest)

  @property
  def info(self):
    return {'yid': self.yid, 'filename': self.filename}
