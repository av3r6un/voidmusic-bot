from aiogram.types import FSInputFile, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from .modules import LinkFilter, CommandFilter, CommandStart
from .modules import VoidMusic, Buttons, Logger
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from .config import Settings
from aiohttp import web
import ssl


router = Router()
settings = Settings()
buttons = Buttons(settings.BUTTONS)
logger = Logger(settings.LOG_FILENAME, settings.DATE_FMT, settings.LOG_FMT)


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
  if activeTube:
    await m.chat.do('typing')
    music = VoidMusic(m.text, logger)
    start_message = await m.answer(f'Начало скачивания {music.title}', reply_markup=ReplyKeyboardRemove())
    await m.chat.do('upload_document')
    path = music.download()
    await start_message.delete()
    await m.answer_document(document=FSInputFile(path))
    global activeTube
    activeTube = False
  else:
    await m.answer(f'Не выбрана команда. Выберите, пожалуйста, команду:', reply_markup=ReplyKeyboardMarkup(keyboard=[[buttons.BUTTON_DOWNLOAD]], resize_keyboard=True))


async def on_startup(bot: Bot) -> None:
  await bot.set_webhook(
    f'{settings.BASE_WEBHOOK_URL}{settings.WEBHOOK_PATH}',
    certificate=FSInputFile(settings.WEBHOOK_SSL_CERT),
    secret_token=settings.WEBHOOK_SECRET,
  )

def main() -> None:
  dp = Dispatcher()
  dp.include_router(router)

  dp.startup.register(on_startup)
  bot = Bot(settings.TOKEN, parse_mode=ParseMode.HTML)

  app = web.Application()
  webhook_req_handler = SimpleRequestHandler(
    dispatcher=dp, bot=bot, secret_token=settings.WEBHOOK_SECRET
  )
  webhook_req_handler.register(app, path=settings.WEBHOOK_PATH)

  setup_application(app, dp, bot=bot)

  context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
  context.load_cert_chain(settings.WEBHOOK_SECRET, settings.WEBHOOK_SSL_PRIV)

  logger.info('Starting app..')
  web.run_app(app, host=settings.WEB_SERVER_HOST, port=settings.WEB_SERVER_PORT, ssl_context=context)


if __name__ == '__main__':
  main()
