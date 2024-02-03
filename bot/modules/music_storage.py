from time import time
import yaml


class FileInfo:
  uid = None
  yid = None
  sent: int = None
  receiver: int = None
  filename: str = None
  
  def __init__(self, uid, yid, receiver, filename, sent=None) -> None:
    self.uid = uid
    self.yid = yid
    self.receiver = receiver
    self.filename = filename
    self.sent = sent if sent else time()
  
  @property
  def json(self):
    return dict(uid=self.uid, yid=self.yid, sent=self.sent, receiver=self.receiver, filename=self.filename)


class CurrentSession:
  opened: int = None
  closed: int = None
  files: list[FileInfo] = []

  def __init__(self, filepath) -> None:
    self.filepath = filepath
    self.opened = time()

  def _load_storage(self):
    with open(self.filepath, 'r', encoding='utf-8') as file:
      data = yaml.safe_load(file)
    if data:
      for file in data:
        self.files.append(FileInfo(**file))

  def _dump_storage(self):
    if self.files:
      storage = [file.json for file in self.files]
      with open(self.filepath, 'w', encoding='utf-8') as file:
        yaml.safe_dump(storage, file)
      return True

  def dump(self):
    self.closed = time()
    self._dump_storage()

  def __getitem__(self, __file):
    if not self.files:
      return None
    for file in self.files:
      if file.yid == __file:
        return file
  
  def renew(self):
    self.closed = None
    self.opened = time()
    self.files = self._load_storage()


class MusicStorage:
  session: CurrentSession = None
  length: int = None

  def __init__(self, filepath):
    self.session = CurrentSession(filepath)
    self.length = len(self.session.files) if self.session.files else 0

  def new_item(self, fileinfo: dict):
    self.session.files.append(FileInfo(**fileinfo))
    self.session.dump()
    self.session.renew()

  def close_(self):
    self.session.dump()

  def __exit__(self):
    self.session.dump()

  
  

