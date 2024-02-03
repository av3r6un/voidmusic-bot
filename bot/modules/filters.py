from aiogram.filters import CommandStart, Filter
from urllib.parse import urlparse


class CommandFilter(Filter):
  def __init__(self, text: str) -> None:
    self.text = text

  async def __call__(self, message) -> bool:
    return message.text == self.text
  

class LinkFilter(Filter):
  DOMAINS = ['www.youtube.com', 'youtube.com', 'youtu.be']

  async def __call__(self, message) -> bool:
    return urlparse(message.text).netloc in self.DOMAINS
