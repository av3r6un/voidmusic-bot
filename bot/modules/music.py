from pytube import YouTube
import ffmpeg
import os


class VoidMusic:
  def __init__(self, link, logger):
    self.logger = logger
    self.yt = YouTube(link)
    self.song = self.yt.streams.filter(only_audio=True, abr=f'{self._get_highest_abr()}').first()
    self.title = self.song.title

  def download(self):
    author = self.yt.author
    filename = f'{self._allowed_filename(author)}-{self._allowed_filename(self.title)}'
    self.song.download(filename=f'{filename}.wav')
    path = self._convert(filename)
    return path  

  def _get_highest_abr(self):
    br = [br.abr for br in self.yt.streams.filter(only_audio=True)]
    i = max([i for i, br in enumerate(br)])
    return br[i]
  
  @staticmethod
  def _allowed_filename(title):
    repl = {' ': '_', ':': '', "'": '', '?': '', '...': '', '/': '', '\\': '', '|': '', '®': '', '•': '', '.': ''}
    return ''.join(repl.get(c, c) for c in title).strip('_')
  
  @staticmethod
  def _convert(filename):
    try:
      proc = (
        ffmpeg
        .input(f'{filename}.wav')
        .output(f'{filename}.mp3', **{'c:a': 'libmp3lame'})
        .overwrite_output()
        .global_args('-loglevel', 'quiet')
        .run_async(pipe_stdout=True)
      )
      proc.wait()
      return f'{filename}.mp3'
    except Exception as ex:
      print(str(ex))
    finally:
      os.remove(f'{filename}.wav')
  