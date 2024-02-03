from datetime import datetime as dt


class Logger:
  def __init__(self, filename, date_fmt, log_fmt) -> None:
    self.filename = filename
    self.date_fmt = date_fmt
    self.log_fmt = log_fmt
    self.separated = False

  def error(self, message) -> None:
    self._make_log('error', message)

  def info(self, message) -> None:
    self._make_log('info', message)
  
  def _separate(self) -> None:
    if not self.separated:
      message = f'{"="*25}\t[Started {dt.now().strftime(self.date_fmt)}]\t{"="*25}\n'
      with open(self.filename, 'a', encoding='utf-8') as file:
        file.write(message)
      self.separated = True

  def _make_log(self, level, message) -> None:
    self._separate()
    time = dt.now().strftime(self.date_fmt)
    msg = self.log_fmt.format(time=time, level=level.upper(), message=message) + '\n'
    with open(self.filename, 'a', encoding='utf-8') as file:
      file.write(msg)
  
