import yaml
import sys
import os


class VoidMusicException(BaseException):
  message = None

  def __init__(self, dep, *args) -> None:
    super().__init__(*args)
    self.messages = self._load_messages(dep)

  @staticmethod
  def _load_messages(dep) -> dict:
    fp = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'messages.yaml')
    try:
      with open(fp, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
      return data[dep]
    except FileNotFoundError:
      print('Exception Messages Not Found.')
      sys.exit(-1)

  def make_error(self, case, error, **kwargs):
    self.message = ' '.join(kwargs.get(word, word) for word in self.messages[case][error].split())
  