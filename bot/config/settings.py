from dotenv import load_dotenv
import yaml
import sys
import os


class Settings:
  ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../')
  STORAGE = os.path.join(ROOT, 'storage')

  def __init__(self) -> None:
    self._initial_start()
    self._init_settings()

  def _initial_start(self) -> None:
    if not os.path.exists(self.STORAGE):
      os.makedirs(self.STORAGE, exist_ok=True)
    
  def _init_settings(self) -> None:
    self._sensitive_info()
    try:
      with open(os.path.join(self.ROOT, 'bot', 'config', 'settings.yaml'), 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
      self.__dict__.update(data)
    except FileNotFoundError:
      print('Config file not found.')
      sys.exit(-1)

  def _sensitive_info(self):
    load_dotenv(os.path.join(self.ROOT, 'bot', 'config', '.env'))
    info = {'TOKEN': os.getenv('TOKEN'), 'WEBHOOK_SSL_CERT': os.getenv('WH_SSL_CERT'), 'WEBHOOK_SSL_PRIV': os.getenv('WH_SSL_PRIV'),
            'WEBHOOK_SECRET': os.getenv('WH_SECRET')}
    self.__dict__.update(info)

  
  