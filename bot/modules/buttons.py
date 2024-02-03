from aiogram.types import KeyboardButton


class Buttons:
  def __init__(self, buttons: dict):
    for name, text in buttons.items():
      self.__dict__[name] = KeyboardButton(text=text)
  