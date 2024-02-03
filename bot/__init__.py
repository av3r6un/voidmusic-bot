from aiogram.types import FSInputFile, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from .modules import VoidMusic, Buttons, Logger, MusicStorage
from .modules import LinkFilter, CommandFilter, CommandStart
from aiogram import Bot, Dispatcher, Router
from .exceptions import DownloadError
from aiogram.enums import ParseMode
from .config import Settings
import asyncio


router = Router()
settings = Settings()
buttons = Buttons(settings.BUTTONS)
logger = Logger(settings.LOG_FILENAME, settings.DATE_FMT, settings.LOG_FMT)
mStorage = MusicStorage(settings.MS_FILEPATH)

@router.message(CommandStart())
async def start_handler(m: Message) -> None:
  await m.answer(f'Привет, {m.from_user.first_name}!', reply_markup=ReplyKeyboardMarkup(keyboard=[[buttons.DOWNLOAD]], resize_keyboard=True))


@router.message(CommandFilter(buttons.DOWNLOAD.text))
async def downloading_handler(m: Message) -> None:
  global activeTube
  activeTube = True
  await m.answer(f'Для продолжения введите ссылку видеохостинга YouTube:', reply_markup=ReplyKeyboardMarkup(keyboard=[[buttons.CANCEL]], resize_keyboard=True))


@router.message(CommandFilter(buttons.CANCEL.text))
async def cancel_handler(m: Message) -> None:
  await m.answer(f'Отмена.', reply_markup=ReplyKeyboardRemove())


@router.message(LinkFilter())
async def searcher(m: Message) -> None:
  global activeTube
  if activeTube:
    await m.chat.do('typing')
    logger.info(f'Received download request from user: {m.from_user.id}')
    music = VoidMusic(m.text, logger, settings)
    already_downloaded = mStorage.session[music.yid]
    if not already_downloaded:
      start_message = await m.answer(f'Начало скачивания {music.title}', reply_markup=ReplyKeyboardRemove())
      try:
        await m.chat.do('upload_document')
        path = music.download()
        await start_message.delete()
        document_message = await m.answer_document(document=FSInputFile(path))
        mStorage.new_item(music.info | {'uid': document_message.document.file_unique_id, 'receiver': m.from_user.id})
        activeTube = False
        music.delete_latest()
      except DownloadError as err:
        await m.answer(text=err.message)
    else:
      m.answer_document(document=already_downloaded.uid)
  else:
    await m.answer(f'Не выбрана команда. Выберите, пожалуйста, команду:', reply_markup=ReplyKeyboardMarkup(keyboard=[[buttons.DOWNLOAD]], resize_keyboard=True))

async def on_shutdown(bot: Bot) -> None:
  mStorage.close_()


async def _main() -> None:
  dp = Dispatcher()
  dp.include_router(router)

  dp.shutdown.register(on_shutdown)
  bot = Bot(settings.TOKEN, parse_mode=ParseMode.HTML)

  await dp.start_polling(bot)

  logger.info('Starting app..')


def main() -> None:
  asyncio.run(_main())


if __name__ == '__main__':
  main()
