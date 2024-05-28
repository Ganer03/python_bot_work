import json
import logging
import asyncio
import aioschedule
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3 as sq
from datetime import *
import pytz
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InputFile, InlineKeyboardButton, \
    InlineKeyboardMarkup, CallbackQuery, InputMedia
from aiogram.types import Message, ShippingOption, ShippingQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.message import ContentType

# itemer_podpiski = {
#     'start': {
#         'item_title': 'Марафон Волна рилсов/Tariff: «Start»',
#         'item_description': 'В подписку входят общие обучения и видео уроки.\nНа протяжении 60 дней тебя ждет увлекательный марафон по спорту и рилсам.\nПрисоединяйся)',
#         'successful_payment': 'Платеж на сумму `{total_amount} {currency}` совершен успешно!\nПоздравляем, нажми /start и вливайся в наш марафон',
#         'cost': 100000
#     },
#     'guest': {
#         'item_title': 'Марафон Волна рилсов/Tariff: «Guest»',
#         'item_description': 'В подписку входят общие обучения и видео уроки + индивидуальная консультация и составленная программа на 60 дней с нутрицологом и тренером.\nНа протяжении 60 дней тебя ждет увлекательный марафон по спорту и рилсам.\nПрисоединяйся)',
#         'successful_payment': 'Платеж на сумму `{total_amount} {currency}` совершен успешно!\nПоздравляем, нажми /start и вливайся в наш марафон',
#         'cost': 500000
#     }
# }
#
# item_url = 'https://static.tildacdn.com/tild3036-6162-4562-b061-616365353430/photo_2023-10-29_23-.jpg'
# item_url1 = 'https://static.tildacdn.com/tild6638-3531-4633-a532-386235366563/photo_2023-11-06_00-.jpg'
# item_url1b = 'AgACAgIAAxkBAAITGGVIB98eWAP4AVfpReBwyrqxpVRnAAJ9zzEbJEVBSvV9mI0tWcDCAQADAgADeQADMwQ'
# photer = 'AgACAgIAAxkBAAMsZeMti6PASGLii2xBrInzk1pKH5UAAlHfMRugxhhLXgyVwILawPcBAAMCAAN4AAM0BA'
photer = 'AgACAgIAAxkBAAICMWXmBjGIb4Gw9zgni78gSOYC2EGPAALR2zEb6EEwSxhhPYX0F0DRAQADAgADeAADNAQ'
pdf_file = 'BQACAgIAAxkBAAIRyWXwcKerUPs7NrsNQhW3-ZsjpY_IAAJ9SQACrPuAS4WORpxEnqQtNAQ'
pdf_file_en = 'BQACAgIAAxkBAAIRzWXwcLiJKtdXl1u_k4v3jyUN0vHoAAJ_SQACrPuAS5XFI6NTRZT_NAQ'
# video_vst = 'BAACAgIAAxkBAAMPZeMpvk9Nmop9vAvVjVwxqMXuk2MAAolCAAJa1xlLPo29fcdJNdg0BA'
video_vst = 'BAACAgIAAxkBAAIZBmXwuPdIHFvBZqLOgc-R68X-rozEAALBRgACdlKIS3rxuMTMGHoqNAQ'
text_vst = 'This is an example of the level of Reels that we will do at the marathon, the creation of this video takes 15 minutes + time to shoot'
text_vst_ru = 'Это пример уровня Reels, который мы будем делать на марафоне, создание этого видео занимает 15 минут + время на съемку.'
video_tg_premiun = 'BAACAgIAAxkBAAIErWVAHPkuHFK66T3c8PDKRW2ijdfBAALxMwACSIkJShTxNUy0SWx4MAQ'
text_tg_premiun = 'Инструкция №1\nкак установить premium аккаунт в Telegram, посмотрите видео инструкцию и повторите действия в программе https://t.me/PremiumBot'
video_tg_premiun1 = 'BAACAgIAAxkBAAIHaGVBbUK2ZBouCU6mZPv8A364ohPTAAJwQAACSIkRSnlkrKc6-EqSMwQ'
text_tg_premiun1 = 'Базовые знания как создать видео с субтитрами'
tek_zad = 0
dop_zad = -1
# 5319695093
video_privet = 'BAACAgIAAxkBAAIF-WXo3CpyP9Y4tyvkG_R26Y_wyS4vAAJsSAACTENISxcAAazhTYiDLTQE'
admin_id = [5319695093, 5761067050]
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
button_1 = types.KeyboardButton(text="/start")
button_2 = types.KeyboardButton(text="/help")
channel_id = -1002099995655
quer = ['Посмотреть задания', 'Выполнить задание', 'Чат', 'Посмотреть рейтинг', 'Уроки', 'Инструкция']


# video_hy = 'BAACAgIAAxkBAAMJZT596G5XVpY1W6I3huMlUvPlJHkAAos6AAKMsfhJZMllr6DNj28wBA'
# text_hy = '''Вступительное задание
#
# “Как заявляешь так и живешь “ с этой фразы я думаю многие согласятся, ведь когда начинаешь новое дело, то для его успеха, конечно нужно оставить робость и сомнения.
# По этому предлагаю заявить о том, что последующие 60 дней, я намерен составить план своей физической программы, следовать ему и выкладывать интересный видео контент в качестве отчета и в регулярном порядке, а если кто заметит что его нет, то это означает одно, что у меня- СРЫВ и я готов платить ЦЕНУ СЛОВА  ( какова цена слова напишите сами, пример какая-то сумма на телефон 5-10 людям написавшим мне, заметив мой СРЫВ, тут ваша фантазия!).
#
# Главная задача заявить о своих действиях, показать готовность делать ежедневные усилия и дать этому «цену слово», обязательно представьтесь , как вас зовут и от куда вы, делаем  видео длительностью не более 1 мин
# Так же сделайте  призыв наблюдателям с просьбой поддержать данный рилс каким-либо комментарием или подтверждением что кто то возьмется за контроль ваш сторис и в случаи вашего СРЫВА сможет указать об этом !!!
#
#
# Текст видео пример:
# Здравствуйте меня зовут Максим я из Саратова, я принимаю участие в спортивном видео марафоне «Волна Рилсов» от Масима Афанасьева начиная с 1 ноября , каждый день я буду получать задания от организатора игры , соотвественно я их выполняю во время, т е  не позднее суток , а в  случаи срыва задания, моей ценой слова будет перевод по 1000₽ трем людям- заместившим отсутствие рилса с отчетом задания , прошу поддержать меня комментариями и подтверждением что ты мой зритель возмешься на контроль мои сторисы , если по истечении 2-3 дней от меня не будет видео- это срыв , пожалуйста сообщи мне об этом и получи от меня 1к₽!'''


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: int | float = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


class FSMFriends(StatesGroup):
    id = State()
    user = State()
    language = State()


class FSMZadan(StatesGroup):
    # number = State()
    date = State()
    text = State()
    language = State()


class FSMLesson(StatesGroup):
    number = State()
    text = State()
    language = State()


class FSMZadanVip(StatesGroup):
    id = State()
    name = State()
    file = State()


class FSMRaiting(StatesGroup):
    name = State()
    raiting = State()


class FSMZadanDop(StatesGroup):
    text = State()
    language = State()


class FSMInstruc(StatesGroup):
    text = State()
    video = State()
    language = State()


class FSMZagotovka(StatesGroup):
    text = State()
    video = State()
    language = State()


class FSMDrop(StatesGroup):
    username = State()
    number = State()
    gooder = State()


class FSMLook(StatesGroup):
    username = State()


async def noon_print(bot=bot):
    try:
        a = cur.execute(f'SELECT name_video,description  FROM zadaniya WHERE number={tek_zad}').fetchone()
        if a:
            d = [row[0] for row in cur.execute(f'SELECT id_akk FROM zad_vip WHERE id_zad={tek_zad}').fetchall()]
            f = cur.execute(f'SELECT id_akk, username, language FROM akk').fetchall()
            at = cur.execute(f'SELECT name_video,description  FROM zadaniya WHERE number={tek_zad} and language="ru"').fetchone()
            ar = cur.execute(f'SELECT name_video,description  FROM zadaniya WHERE number={tek_zad} and language="en"').fetchone()
            for i in f:
                if i[0] not in d:
                    if i[2] == 'ru':
                        a = at
                        text = f'Задание на сегодня: {tek_zad}\n'
                    else:
                        a = ar
                        text = f'Task on today: {tek_zad}\n'
                    if a[0] != '-1000':
                        if a[0].split("^")[0] == 'photo':
                            try:
                                await bot.send_photo(i[0], photo=a[0].split("^")[1])
                            except Exception as e:
                                print(e)
                        else:
                            if a[0].split('^')[0] == 'file':
                                try:
                                    await bot.send_document(channel_id, document=a[1].split('^')[1])
                                except Exception as e:
                                    print(e)
                            else:
                                try:
                                    await bot.send_video(i[0], video=a[0])
                                except Exception as e:
                                    print(e)
                    if a[1] != '':
                        text += a[1]
                    try:
                        await bot.send_message(i[0], text=text)
                    except Exception as e:
                        print(e)
        else:
            await bot.send_message(admin_id[0], text='Задания закончились!!!')
    except Exception as e:
        print(e)


async def noon_print1(bot=bot):
    global tek_zad
    try:
        a = cur.execute(f'SELECT name_video,description  FROM zadaniya WHERE number={tek_zad}').fetchone()
        if a:
            d = [row[0] for row in cur.execute(f'SELECT id_akk FROM zad_vip WHERE id_zad={tek_zad}').fetchall()]
            f = cur.execute(f'SELECT id_akk, username, language FROM akk').fetchall()
            at = cur.execute(
                f'SELECT name_video,description  FROM zadaniya WHERE number={tek_zad} and language="ru"').fetchone()
            ar = cur.execute(
                f'SELECT name_video,description  FROM zadaniya WHERE number={tek_zad} and language="en"').fetchone()
            for i in f:
                if i[0] not in d:
                    if i[2] == 'ru':
                        a = at
                        text = f'Задание на сегодня почти просрочилось: {tek_zad}\nУ вас осталось 2 часа\n'
                    else:
                        a = ar
                        text = f'The task for today is almost overdue: {tek_zad}\nYou have 2 hours left\n'
                    if a[0] != '-1000':
                        if a[0].split("^")[0] == 'photo':
                            try:
                                await bot.send_photo(i[0], photo=a[0].split("^")[1])
                            except Exception as e:
                                print(e)
                        else:
                            if a[0].split('^')[0] == 'file':
                                try:
                                    await bot.send_document(channel_id, document=a[1].split('^')[1])
                                except Exception as e:
                                    print(e)
                            else:
                                try:
                                    await bot.send_video(i[0], video=a[0])
                                except Exception as e:
                                    print(e)
                    if a[1] != '':
                        text += a[1]
                    try:
                        await bot.send_message(i[0], text=text)
                    except Exception as e:
                        print(e)
        else:
            await bot.send_message(admin_id[0], 'Задания закончились!!!')
    except Exception as e:
        print(e)


async def noon_print2(bot=bot):
    global tek_zad
    try:
        print('hi')
        a = cur.execute(f'SELECT name_video,description  FROM zadaniya WHERE number={tek_zad + 1}').fetchone()
        if a:
            cur.execute(f'UPDATE tek_zad set id_tek_zad={tek_zad + 1}')
            base.commit()
            tek_zad += 1
        else:
            await bot.send_message(admin_id[0], 'Задания закончились!!!')
    except Exception as e:
        print(e)


async def noon_print4(bot=bot):
    global dop_zad
    try:
        base.execute(f'DELETE FROM tek_zad_dop WHERE id_tek_zad={dop_zad}')
        cur.execute(f'UPDATE dop_number set id_tek_zad={dop_zad - 1} WHERE id=1')
        base.commit()
        dop_zad -= 1
    except Exception as e:
        print(e)


async def noon_print5(bot=bot):
    try:
        f = cur.execute(f'SELECT id_akk, language FROM akk').fetchall()
        photo_ru = 'AgACAgIAAxkBAAKNUWX4dQV4_kOfsEWJUQFlGjN4LcltAAI82DEbrxTJS-L9Xi10CqnUAQADAgADeQADNAQ'
        photo_en = 'AgACAgIAAxkBAAKNTWX4dQJX4OYehZyNI_0UmrnwWvrUAAI72DEbrxTJS-tjB_tzLKe5AQADAgADeQADNAQ'
        text_ru = '''Участвуй в игре 🎮 начать можно в любой день и догнать группу, все задания и уроки сохраняются, можно выполнить их тогда когда удобно и позволяет время, такого не было ранее ни в одном проекте, я не видел чтобы обучение давалось в подарок и ещё за это вам гарантированно начислили награду в виде монет Laika) 
        Когда Laika будет расти в цене, то многие будут жалеть что не использовали эту возможность, так посмотри глазами себя в будущем, оборачиваясь назад, что бы ты сделал ? Увидимся в игре !!!
        Подключайтесь в чат, там идёт активное общение https://t.me/Laika_storis'''
        text_en = '''Participate in the game 🎮 you can start any day and catch up with the group, all tasks and lessons are saved, you can complete them when it is convenient and time allows, this has not happened before in any project, I have not seen that training was given as a gift and for this you are guaranteed to receive a reward in the form of Laika coins) When Laika will grow in price, then many will regret that they did not use this opportunity, so look at yourself in the future, looking back, what would you do? See you in the game!!! Connect to the chat, there is an active communication going on https://t.me/Laika_storis'''
        for i in f:
            if i[1] == 'ru':
                try:
                    await bot.send_photo(i[0], photo=photo_ru, caption=text_ru)
                except Exception as e:
                    print(e)
            else:
                try:
                    await bot.send_photo(i[0], photo=photo_en, caption=text_en)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)


def sql_start():
    global base, cur, tek_zad, dop_zad
    base = sq.connect('bot.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    # base.execute('DROP TABLE zad_vip')
#    base.execute('DROP TABLE tek_zad_dop')
    # base.execute('UPDATE akk set raiting=0 WHERE id==1')
    # base.execute('DELETE FROM akk WHERE id==9')
    base.execute('CREATE TABLE IF NOT EXISTS zadaniya(id INTEGER PRIMARY KEY, number INTEGER, name_video varchar(20),'
                 'description varvchar(20), language varvchar(20), date varchar(20))')
    base.execute('CREATE TABLE IF NOT EXISTS instruct(id INTEGER PRIMARY KEY, number INTEGER, name_video varchar(20),'
                 'description varvchar(20), name varchar(20), language varchar(20))')
    base.execute('CREATE TABLE IF NOT EXISTS zagatovka(id INTEGER PRIMARY KEY, number INTEGER, name_video varchar(20),'
                 'description varvchar(20), name varchar(20), language varchar(20))')
    base.execute(
        'CREATE TABLE IF NOT EXISTS akk(id INTEGER PRIMARY KEY, id_akk INTEGER, raiting INTEGER, username varchar(20), language varchar(20))')
    base.execute(
        'CREATE TABLE IF NOT EXISTS drop_zad(id INTEGER PRIMARY KEY, id_akk INTEGER, id_zad INTEGER, username varchar(20), ball INTEGER)')
    base.execute(
        'CREATE TABLE IF NOT EXISTS parashut(id INTEGER PRIMARY KEY, id_akk INTEGER, col INTEGER)')
    base.execute(
        'CREATE TABLE IF NOT EXISTS zad_vip(id INTEGER PRIMARY KEY, id_akk INTEGER, id_zad INTEGER, description varchar(20), video_id varchar(20), checker INTEGER)')
    base.execute(
        'CREATE TABLE IF NOT EXISTS lessons(id INTEGER PRIMARY KEY, number INTEGER, name_video varchar(20), description varvchar(20), language varvchar(20))')
    base.execute('CREATE TABLE IF NOT EXISTS tek_zad(id INTEGER PRIMARY KEY, id_tek_zad INTEGER)')
    base.execute(
        'CREATE TABLE IF NOT EXISTS tek_zad_dop(id INTEGER PRIMARY KEY, id_tek_zad INTEGER, name_video varchar(20), description varvchar(20), language varvchar(20), date_hour integer, date_minute integer)')
    base.execute('CREATE TABLE IF NOT EXISTS dop_number(id INTEGER PRIMARY KEY, id_tek_zad INTEGER)')
    base.execute(
        'CREATE TABLE IF NOT EXISTS dop_vip(id INTEGER PRIMARY KEY, id_akk INTEGER, id_zad INTEGER, description varchar(20), video_id varchar(20), checker INTEGER)')
    # cur.execute(f'DELETE FROM akk WHERE username="@pian_rom"')
    # rtb = cur.execute(f'SELECT id_akk,username from akk where username="@pian_rom"').fetchall()
    # for i in rtb:
    #     cur.execute(f'DELETE FROM parashut WHERE id_akk={i[0]}')
    # base.execute(
    #     f'INSERT INTO dop_vip(id_akk, id_zad, description, video_id, checker) VALUES (842163286, -1, "HI", "-1000", 0)')
    # base.execute('INSERT INTO dop_number(id_tek_zad) VALUES (-1)')
    # a = cur.execute('SELECT id_akk FROM akk').fetchall()
    # for i in a:
    #     cur.execute(f'INSERT INTO parashut(id_akk, col) VALUES ({i[0]}, 3)')
    base.commit()
    try:
        if cur.execute('SELECT id_tek_zad FROM tek_zad').fetchone()[0]:
            tek_zad = cur.execute('SELECT id_tek_zad FROM tek_zad').fetchone()[0]
    except Exception as e:
        print(e)
    try:
        if cur.execute('SELECT id_tek_zad FROM dop_number').fetchone()[0]:
            dop_zad = cur.execute('SELECT id_tek_zad FROM dop_number').fetchone()[0]
    except Exception as e:
        print(e)


async def on_startup(_):
    pass
    # schedulerer = AsyncIOScheduler(timezone='Asia/Dubai')
    # schedulerer.add_job(noon_print, trigger='cron', hour=10, minute=00, start_date=datetime.now().date(),
    #                     kwargs={'bot': bot})
    # schedulerer.add_job(noon_print1, trigger='cron', hour=20, minute=00, start_date=datetime.now().date(),
    #                     kwargs={'bot': bot})
    # schedulerer.add_job(noon_print2, trigger='cron', hour=9, minute=40, start_date=datetime.now().date(),
    #                     kwargs={'bot': bot})
    # schedulerer.add_job(noon_print5, trigger='cron', hour=12, minute=00, start_date=datetime.now().date(),
    #                     kwargs={'bot': bot})
    # schedulerer.add_job(noon_print5, trigger='cron', hour=21, minute=00, start_date=datetime.now().date(),
    #                     kwargs={'bot': bot})
    # schedulerer.start()


# @dp.message_handler(content_types=['photo', 'audio', 'video', 'document'])
# async def get_message(message: types.Message, album: list[types.Message] = None):
#     # if message.chat.id not in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()] and message.chat.id != channel_id:
#     if message.chat.id > 0:
#         if not album:
#             album = [message]
#
#         media_group = types.MediaGroup()
#         for obj in album:
#             if obj.photo:
#                 file_id = obj.photo[-1].file_id
#             else:
#                 file_id = obj[obj.content_type].file_id
#             try:
#                 if obj == album[-1]:
#                     a = ''
#                     if not(album[0].caption is None):
#                         a = album[0].caption
#                     text = f'@{message.from_user.username}\n' + a + f'\n<code>/chat_{message.from_user.id}_{message.message_id}_</code>\n<code>/blocked_{message.from_user.id}</code>'
#                     media_group.attach(InputMedia(media=file_id,
#                                                   type=obj.content_type,
#                                                   caption=text,
#                                                   parse_mode="html"))
#                 else:
#                     media_group.attach(InputMedia(media=file_id, type=obj.content_type))
#             except ValueError:
#                 return await message.answer("This type of album is not supported by aiogram.")
#         await bot.send_media_group(message.chat.id, media_group)
#         await bot.send_message(message.chat.id, text=media_group)
#         print(media_group)
#         # await bot.send_media_group(channel_id, media_group)
#         await message.reply('Ваше сообщение передано в поддержку, ожидайте, скоро поступит ответ')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    if message.chat.id in admin_id:
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
        but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
        but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
        but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
        but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
        but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
        but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
        but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
        but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
        but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
        but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
        but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
        but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
        but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
        keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
        keyboard_inline.insert(
            KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
        await message.answer('Привет админ', reply_markup=keyboard_inline)
    else:
        if message.chat.id not in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
            keyboard_inline = InlineKeyboardMarkup(row_width=1)
            Buter1 = InlineKeyboardButton(text="Русский", callback_data=f"podpt_ru")
            Buter2 = InlineKeyboardButton(text="English", callback_data=f"podpt_en")
            keyboard_inline.add(Buter1, Buter2)
            await bot.send_photo(message.chat.id, photo=photer, reply_markup=keyboard_inline,
                                 caption='Выберите язык/Choose the language')
            # await bot.send_message(message.chat.id, reply_markup=keyboard_inline, text='Выберите язык/Choose the language')
        else:
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            if cur.execute(f'SELECT language FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()[0] == 'ru':
                but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
                but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
                but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
                but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
                but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
                but6 = KeyboardButton(text="Чат")
                but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
                but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
                keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                await bot.send_photo(message.chat.id,
                                     caption='''Добро пожаловать на марафон, кликай по кнопкам и узнавай полезную информацию''',
                                     reply_markup=keyboard_inline, photo=photer)

            else:
                but1 = KeyboardButton(text="Complete the task", callback_data=f"zadaniye_vip")
                but2 = KeyboardButton(text="View tasks", callback_data=f"zadaniye_look")
                but3 = KeyboardButton(text="View the rating", callback_data=f"zadaniye_lookppp")
                but4 = KeyboardButton(text="Lessons", callback_data=f"zadaniye_lesson")
                but5 = KeyboardButton(text="Instruction", callback_data=f"zadaniye_lesson")
                but6 = KeyboardButton(text="Chat")
                but7 = KeyboardButton(text="Change the language", callback_data=f"zadaniye_lesson")
                but8 = KeyboardButton(text="Blanks", callback_data=f"zadaniye_lesson")
                keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                # await bot.send_video(message.chat.id, video=video_hy)
                await bot.send_photo(message.chat.id,
                                     caption='''Welcome to the marathon, click on the buttons and find out useful information''',
                                     reply_markup=keyboard_inline, photo=photer)
            # await message.answer(
            #     '''Добро пожаловать на марафон, кликай по кнопкам и узнавай полезную информацию, а также не забудь пройти нулевое задание''',
            #     reply_markup=keyboard_inline1)


# , в данный момент прямая оплата не настроена, поэтому оплата будет происходить через меня - @maks_afanasiev\n
#     Или заполни анкету на участие в марафоне и с тобой свяжется наш админ 🧑🏻‍💻 https://kurl.ru/bqqhx
# @dp.message_handler(content_types=['photo'])
# async def load_name(message: types.Message):
#     if message.chat.id in admin_id:
#         file_id = message.photo[-1].file_id
#         print(file_id)


@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.chat.id in [row[0] for row in
                           cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        if cur.execute(f'SELECT language FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()[0] == 'ru':
            but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
            but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="Чат")
            but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
            keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
            await state.finish()
            await message.reply('Все состояния сброшены', reply_markup=keyboard_inline)
        else:
            but1 = KeyboardButton(text="Complete the task", callback_data=f"zadaniye_vip")
            but2 = KeyboardButton(text="View tasks", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="View the rating", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="Lessons", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="Instruction", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="Chat")
            but7 = KeyboardButton(text="Change the language", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="Blanks", callback_data=f"zadaniye_lesson")
            keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
            await state.finish()
            await message.reply('All states are reset', reply_markup=keyboard_inline)
    else:
        if message.chat.id in admin_id:
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(
                KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Все состояния сброшены', reply_markup=keyboard_inline)
            await state.finish()
        else:
            await state.finish()
            await message.reply('Все состояния сброшены')


@dp.message_handler(commands='add_zagatovka')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        butomer1 = KeyboardButton(text="ru", callback_data=f"")
        butomer2 = KeyboardButton(text="en", callback_data=f"")
        keyboard_inline.add(butomer1, butomer2)
        keyboard_inline.insert(
            KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
        await message.answer('Введите язык заготовки ru или en или /cancel', reply_markup=keyboard_inline)
        await FSMZagotovka.language.set()


@dp.message_handler(state=FSMZagotovka.language)
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        async with state.proxy() as data:
            data['language'] = message.text
        await message.answer('Введите название заготовки или /cancel')
        await FSMZagotovka.text.set()


@dp.message_handler(state=FSMZagotovka.text)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            async with state.proxy() as data:
                data['text'] = message.text

            await message.answer('Отправьте заготовку: видео и текст или просто текст или фото или файл ')
            await FSMZagotovka.next()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMZagotovka.video, content_types=['video'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            r = data["text"]
            l = data['language']
            file_id = message.video.file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute(
                f'INSERT INTO zagatovka(number, name_video, description, name, language) VALUES ({0}, "{file_id}","{kr}", "{r}", "{l}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Заготовка добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMZagotovka.video, content_types=['photo'])
async def get_message(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            r = data["text"]
            l = data['language']
            file_id = 'photo<>' + message.photo[-1].file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute(
                f'INSERT INTO zagatovka(number, name_video, description, name, language) VALUES ({0}, "{file_id}","{kr}", "{r}", "{l}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Заготовка добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMZagotovka.video, content_types=['document'])
async def get_message(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            r = data["text"]
            l = data['language']
            file_id = 'file<>' + message.document.file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute(
                f'INSERT INTO zagatovka(number, name_video, description, name, language) VALUES ({0}, "{file_id}","{kr}", "{r}", "{l}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Заготовка добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMZagotovka.video, content_types=['audio'])
async def get_message(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            r = data["text"]
            l = data['language']
            file_id = 'audio<>' + message.audio.file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute(
                f'INSERT INTO zagatovka(number, name_video, description, name, language) VALUES ({0}, "{file_id}","{kr}", "{r}", "{l}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Заготовка добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMZagotovka.video, content_types=['text'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            r = data["text"]
            l = data['language']
            file_id = '-1000'
            kr = ''
            if not (message.text is None):
                kr = message.text
            cur.execute(
                f'INSERT INTO zagatovka(number, name_video, description, name, language) VALUES ({0}, "{file_id}","{kr}", "{r}", "{l}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Заготовка добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(commands='add_instrukciya')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        butomer1 = KeyboardButton(text="ru", callback_data=f"")
        butomer2 = KeyboardButton(text="en", callback_data=f"")
        keyboard_inline.add(butomer1, butomer2)
        keyboard_inline.insert(
            KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
        await message.answer('Введите язык инструкции ru или en или /cancel', reply_markup=keyboard_inline)
        await FSMInstruc.language.set()


@dp.message_handler(state=FSMInstruc.language)
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        async with state.proxy() as data:
            data['language'] = message.text
        await message.answer('Введите название интсрукции или /cancel')
        await FSMInstruc.text.set()


@dp.message_handler(state=FSMInstruc.text)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            async with state.proxy() as data:
                data['text'] = message.text

            await message.answer('Отправьте инструкцию: видео и текст или просто текст ')
            await FSMInstruc.next()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMInstruc.video, content_types=['video'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            r = data["text"]
            l = data['language']
            file_id = message.video.file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute(
                f'INSERT INTO instruct(number, name_video, description, name, language) VALUES ({0}, "{file_id}","{kr}", "{r}", "{l}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Инструкция добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMInstruc.video, content_types=['photo'])
async def get_message(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            r = data["text"]
            l = data['language']
            file_id = 'photo<>' + message.photo[-1].file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute(
                f'INSERT INTO instruct(number, name_video, description, name, language) VALUES ({0}, "{file_id}","{kr}", "{r}", "{l}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Инструкция добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMInstruc.video, content_types=['document'])
async def get_message(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            r = data["text"]
            l = data['language']
            file_id = 'file<>' + message.document.file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute(
                f'INSERT INTO instruct(number, name_video, description, name, language) VALUES ({0}, "{file_id}","{kr}", "{r}", "{l}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Инструкция добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMInstruc.video, content_types=['text'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            r = data["text"]
            l = data['language']
            file_id = '-1000'
            kr = ''
            if not (message.text is None):
                kr = message.text
            cur.execute(
                f'INSERT INTO instruct(number, name_video, description, name, language) VALUES ({0}, "{file_id}","{kr}", "{r}", "{l}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Инструкция добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(commands='add_pashalka')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        butomer1 = KeyboardButton(text="ru", callback_data=f"")
        butomer2 = KeyboardButton(text="en", callback_data=f"")
        keyboard_inline.add(butomer1, butomer2)
        keyboard_inline.insert(
            KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
        await message.answer('Введите язык пасхалки ru или en или /cancel', reply_markup=keyboard_inline)
        await FSMZadanDop.language.set()


@dp.message_handler(state=FSMZadanDop.language)
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        async with state.proxy() as data:
            data['language'] = message.text
        await message.answer('Отправьте задание или нажмите /cancel')
        await FSMZadanDop.text.set()


@dp.message_handler(state=FSMZadanDop.text, content_types=['photo'])
async def get_message(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            l = data['language']
            file_id = 'photo^' + message.photo[-1].file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            base.execute(f'DELETE FROM tek_zad_dop WHERE id_tek_zad={dop_zad} and language="{l}"')
            a = cur.execute(f'SELECT id_tek_zad FROM dop_number').fetchone()[0]
#                base.execute(
#        'CREATE TABLE IF NOT EXISTS tek_zad_dop(id INTEGER PRIMARY KEY, id_tek_zad INTEGER, name_video varchar(20), description varvchar(20), language varvchar(20), date_hour integer, date_minute integer)')
            hour = datetime.now(pytz.timezone('Europe/Moscow')).hour
            minute = datetime.now(pytz.timezone('Europe/Moscow')).minute
            cur.execute('insert into tek_zad_dop(id_tek_zad, name_video, description, language, date_hour, date_minute) values (?,?,?,?,?,?)',
                        (a, file_id, kr, l, int(hour), int(minute)))
            base.commit()
            if l == "ru":
                try:
                    schedulerer1 = AsyncIOScheduler(timezone='Europe/Moscow')
                    schedulerer1.add_job(noon_print4, trigger='date', run_date=datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=6),
                                         kwargs={'bot': bot})
                    schedulerer1.start()
                except Exception as e:
                    print(e)
            await message.answer(f'Задание добавлено, ее номер {dop_zad}')
            f = cur.execute(f'SELECT id_akk, username, language FROM akk').fetchall()
            for i in f:
                try:
                    a = cur.execute(
                        f'SELECT name_video,description  FROM tek_zad_dop WHERE id_tek_zad={dop_zad} and language="{i[2]}"').fetchone()
                    if l == i[2]:
                        if i[2] == "ru":
                            text = f'Пасхалочное задание на сегодня: {dop_zad}\n'
                        else:
                            text = f'Easter task on today: {dop_zad}\n'
                        if a[0] != '-1000':
                            if a[0].split("^")[0] == 'photo':
                                await bot.send_photo(i[0], photo=a[0].split("^")[1])
                            else:
                                try:
                                    await bot.send_video(i[0], video=a[0])
                                except Exception as e:
                                    print(e)
                        if a[1] != '':
                            text += a[1]
                        try:
                            await bot.send_message(i[0], text=text)
                        except Exception as e:
                            print(e)
                except Exception as e:
                    print(e)
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer(f'Задание разослано', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Какая-то ошибка, попробуйте еще раз', reply_markup=keyboard_inline)


@dp.message_handler(state=FSMZadanDop.text, content_types=['video'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            l = data['language']
            file_id = message.video.file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            base.execute(f'DELETE FROM tek_zad_dop WHERE id_tek_zad={dop_zad} and language="{l}"')
            a = cur.execute(f'SELECT id_tek_zad FROM dop_number').fetchone()[0]
            hour = datetime.now(pytz.timezone('Europe/Moscow')).hour
            minute = datetime.now(pytz.timezone('Europe/Moscow')).minute
            cur.execute('insert into tek_zad_dop(id_tek_zad, name_video, description, language, date_hour, date_minute) values (?,?,?,?,?,?)',
                        (a, file_id, kr, l, int(hour), int(minute)))
            base.commit()
            if l == "ru":
                try:
                    schedulerer1 = AsyncIOScheduler(timezone='Europe/Moscow')
                    schedulerer1.add_job(noon_print4, trigger='date', run_date=datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=6),
                                         kwargs={'bot': bot})
                    schedulerer1.start()
                except Exception as e:
                    print(e)
            await message.answer(f'Задание добавлено, ее номер {dop_zad}')
            f = cur.execute(f'SELECT id_akk, username, language FROM akk').fetchall()
            for i in f:
                try:
                    a = cur.execute(
                        f'SELECT name_video,description  FROM tek_zad_dop WHERE id_tek_zad={dop_zad} and language="{i[2]}"').fetchone()
                    if l == i[2]:
                        if i[2] == "ru":
                            text = f'Пасхалочное задание на сегодня: {dop_zad}\n'
                        else:
                            text = f'Easter task on today: {dop_zad}\n'
                        if a[0] != '-1000':
                            if a[0].split("^")[0] == 'photo':
                                await bot.send_photo(i[0], photo=a[0].split("^")[1])
                            else:
                                try:
                                    await bot.send_video(i[0], video=a[0])
                                except Exception as e:
                                    print(e)
                        if a[1] != '':
                            text += a[1]
                        try:
                            await bot.send_message(i[0], text=text)
                        except Exception as e:
                            print(e)
                except Exception as e:
                    print(e)
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer(f'Задание разослано', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Какая-то ошибка, попробуйте еще раз', reply_markup=keyboard_inline)


@dp.message_handler(state=FSMZadanDop.text, content_types=['text'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            l = data['language']
            base.execute(f'DELETE FROM tek_zad_dop WHERE id_tek_zad={dop_zad} and language="{l}"')
            a = cur.execute(f'SELECT id_tek_zad FROM dop_number').fetchone()[0]
            hour = datetime.now(pytz.timezone('Europe/Moscow')).hour
            minute = datetime.now(pytz.timezone('Europe/Moscow')).minute
            cur.execute('insert into tek_zad_dop(id_tek_zad, name_video, description, language, date_hour, date_minute) values (?,?,?,?,?,?)',
                        (a, "-1000", message.text, l, int(hour), int(minute)))
#            cur.execute('insert into tek_zad_dop(id_tek_zad, name_video, description, language) values (?,?,?,?)',
#                        (a, "-1000", message.text, l))
            base.commit()
            if l == "ru":
                try:
                    schedulerer1 = AsyncIOScheduler(timezone='Europe/Moscow')
                    schedulerer1.add_job(noon_print4, trigger='date', run_date=datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=6),
                                         kwargs={'bot': bot})
                    schedulerer1.start()
                except Exception as e:
                    print(e)
            await message.answer(f'Задание добавлено, ее номер {dop_zad}')
            f = cur.execute(f'SELECT id_akk, username, language FROM akk').fetchall()
            for i in f:
                try:
                    a = cur.execute(
                        f'SELECT name_video,description  FROM tek_zad_dop WHERE id_tek_zad={dop_zad} and language="{i[2]}"').fetchone()
                    if l == i[2]:
                        if i[2] == "ru":
                            text = f'Пасхалочное задание на сегодня: {dop_zad}\n'
                        else:
                            text = f'Easter task on today: {dop_zad}\n'
                        if a[0] != '-1000':
                            if a[0].split("^")[0] == 'photo':
                                await bot.send_photo(i[0], photo=a[0].split("^")[1])
                            else:
                                try:
                                    await bot.send_video(i[0], video=a[0])
                                except Exception as e:
                                    print(e)
                        if a[1] != '':
                            text += a[1]
                        try:
                            await bot.send_message(i[0], text=text)
                        except Exception as e:
                            print(e)
                except Exception as e:
                    print(e)
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer(f'Задание разослано', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Какая-то ошибка, попробуйте еще раз', reply_markup=keyboard_inline)

# @dp.message_handler(commands='check_pashal')
# async def register_friends_hourss(message: types.Message):
#     if message.chat.id in admin_id:
#         try:
#             a = message.text.split(" ")
#             raiting = cur.execute(f'SELECT raiting FROM akk WHERE  id_akk=={int(a[1])}').fetchone()[0]
#             cur.execute(f'UPDATE akk set raiting={raiting + int(a[3])} WHERE id_akk=={int(a[1])}')
#             cur.execute(f'UPDATE dop_number set checker=1 WHERE id_akk=={int(a[1])} and id_zad={int(a[2])}')
#             base.commit()
#             await bot.send_message(message.chat.id, text=f'Задание успешно проверено')
#         except Exception as e:
#             await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(commands='check_pashalka')
async def register_friends_hourss(message: types.Message):
    if message.chat.id in admin_id:
        try:
            a = cur.execute(f'SELECT id_akk,id_zad, description, video_id FROM dop_vip WHERE checker={0}').fetchone()
            b = cur.execute(f'SELECT username FROM akk WHERE id_akk={a[0]}').fetchone()
            text = f'{b[0]}\nЗадание:{a[1]}\nОписание:{a[2]}'
            await bot.send_message(message.chat.id, text=text)
            print(a[3])
            if a[3] != '-1000':
                if a[3].split('<>')[0] == 'photo':
                    try:
                        await bot.send_photo(message.chat.id, photo=a[3].split('<>')[1])
                    except Exception as e:
                        print(e)
                else:
                    try:
                        await bot.send_video(message.chat.id, video=a[3])
                    except Exception as e:
                        print(e)
                # await bot.send_video(message.chat.id, video=a[3])
            await bot.send_message(message.chat.id, text=f'/checker {a[0]} {a[1]} ball')
        except Exception as e:
            await message.answer('Все задания проверены')


@dp.message_handler(commands='checker')
async def register_friends_hourss(message: types.Message):
    if message.chat.id in admin_id:
        # try:
        a = message.text.split(" ")
        raiting = cur.execute(f'SELECT raiting FROM akk WHERE  id_akk=={int(a[1])}').fetchone()[0]
        cur.execute(f'UPDATE akk set raiting={raiting + int(a[3])} WHERE id_akk=={int(a[1])}')
        cur.execute(f'UPDATE dop_vip set checker=1 WHERE id_akk={int(a[1])} and id_zad={int(a[2])}')
        base.commit()
        await bot.send_message(message.chat.id, text=f'Задание успешно проверено')
    # except Exception as e:
    #     await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(commands='check_top')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        a = cur.execute(f'SELECT raiting,username, id_akk FROM akk ORDER BY raiting DESC').fetchall()
        b = int(len(a))
        if not (int(len(a)) is int):
            b = int(len(a))
        text = f'Топ игроков, выполневших все задания:\n________Топ 10________\n'
        k = 0
        d = 0
        # raiter = 0
        # flag = 1
        for i in range(b):
            zad = cur.execute(
                f'SELECT * FROM (SELECT id_zad, id_akk FROM zad_vip WHERE id_akk="{a[i][2]}") zv LEFT JOIN (SELECT id_zad,id_akk,ball FROM drop_zad WHERE id_akk="{a[i][2]}") dz ON zv.id_zad=dz.id_zad').fetchall()
            # zad1 = cur.execute(
            #     f'SELECT * FROM (SELECT id_zad, id_akk FROM dop_vip WHERE id_akk={a[i][1]}) zv LEFT JOIN (SELECT id_zad,id_akk,ball FROM drop_zad WHERE id_akk={a[i][1]}) dz ON zv.id_zad=dz.id_zad').fetchall()
            if len(zad) >= 31 or a[i][1] == '@skysadko':
                # await message.answer(str(zad))
                if k == 50:
                    k = 0
                    await message.answer(text)
                # if 2350 <= raiter and 2350 >= a[i][0] and flag:
                #     text += '@pian_rom(842163286) - 2350\n'
                #     k += 1
                #     d += 1
                #     flag = 0
                # else:
                #     raiter = a[i][0]
                if k == 10:
                    text += '______________________\n'
                text += f'{a[i][1]}({a[i][2]}) - {a[i][0]}\n'
                k += 1
                d += 1
        text += f'Кол-во: {d}'
        await message.answer(text)


@dp.message_handler(commands='check_people')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        await message.answer('Введите username\nПример: @pian_rom')
        await FSMLook.username.set()


@dp.message_handler(state=FSMLook.username)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            text = 'Выполненные задания:\n'
            try:
                akk = cur.execute(f'SELECT id_akk FROM akk WHERE username="{message.text}"').fetchone()[0]
            except Exception as e:
                await message.answer('Такого пользователя нет, проверьте, возможно его аккаунт записан в боте как @891323213 или что-то типо такого')
                print(e)
            # zad1 = cur.execute(
            #     f'SELECT id_zad, id_akk FROM zad_vip WHERE id_akk={akk}').fetchall()
            # zad3 = cur.execute(
            #     f'SELECT id_zad, id_akk FROM dop_vip WHERE id_akk={akk}').fetchall()
            # print(zad1)
            # print(zad3)
            # zad2 = cur.execute(
            #     f'SELECT id_zad,id_akk,ball FROM drop_zad WHERE id_akk={akk}').fetchall()
            # print(zad2)
            try:
                zad = cur.execute(f'SELECT * FROM (SELECT id_zad, id_akk FROM zad_vip WHERE id_akk={akk}) zv LEFT JOIN (SELECT id_zad,id_akk,ball FROM drop_zad WHERE id_akk={akk}) dz ON zv.id_zad=dz.id_zad').fetchall()
                zad1 = cur.execute(f'SELECT * FROM (SELECT id_zad, id_akk FROM dop_vip WHERE id_akk={akk}) zv LEFT JOIN (SELECT id_zad,id_akk,ball FROM drop_zad WHERE id_akk={akk}) dz ON zv.id_zad=dz.id_zad').fetchall()
                r = 0
                for i in zad1:
                    r += 1
                    if r > 40:
                        await message.answer(text)
                        text = 'Выполненные задания:\n'
                        r = 0
                    if i[4] != '' and i[4] != None and i[4] != 'None':
                        text += 'Задание ' + str(i[0]) + ' : ' + str(i[4]) + '\n'
                    else:
                        text += 'Задание ' + str(i[0]) + '\n'
                for i in zad:
                    if r > 40:
                        await message.answer(text)
                        text = 'Выполненные задания:\n'
                        r = 0
                    if i[4] != '' and i[4] != None and i[4] != 'None':
                        text += 'Задание ' + str(i[0]) + ' : ' + str(i[4]) + '\n'
                    else:
                        text += 'Задание ' + str(i[0]) + '\n'
            except Exception as e:
                print(e)
            await message.answer(text)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(commands='drop_zadaniye')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        await message.answer('Введите username\nПример: @pian_rom')
        await FSMDrop.username.set()


@dp.message_handler(state=FSMDrop.username)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        async with state.proxy() as data:
            data['username'] = message.text
        await message.answer('Введите номер задания которое хотите удалить\nПример: 0')
        await FSMDrop.number.set()


@dp.message_handler(state=FSMDrop.number)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        async with state.proxy() as data:
            data['number'] = message.text
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        but1 = KeyboardButton(text="Да", callback_data=f"zadaniye_vip")
        but2 = KeyboardButton(text="Нет", callback_data=f"zadaniye_look")
        keyboard_inline.add(but1, but2)
        texter = 'Вы точно хотите удалить это задание?\n'
        await message.answer(text=texter, reply_markup=keyboard_inline)
        await FSMDrop.gooder.set()


@dp.message_handler(state=FSMDrop.gooder)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
        but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
        but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
        but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
        but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
        but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
        but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
        but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
        but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
        but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
        but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
        but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
        but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
        keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13)
        keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
        if message.text == 'Да':
            data = await state.get_data()
            a = data["username"]
            number = int(data["number"])
            try:
                try:
                    b = cur.execute(f'SELECT raiting, id_akk, language FROM akk WHERE username="{a}"').fetchone()
                except Exception as e:
                    await message.answer('Такого username нет в базе', reply_markup=keyboard_inline)
                    await state.finish()
                try:
                    c = cur.execute(f'SELECT ball FROM drop_zad WHERE username="{a}" and id_zad={number}').fetchone()[0]
                except Exception as e:
                    await message.answer(
                        'Данное задание либо было добавлено до изменений в боте, либо человек не выполнял это задание, либо неправильно введен username', reply_markup=keyboard_inline)
                    await state.finish()
                cur.execute(f'DELETE FROM drop_zad WHERE username="{a}" and id_zad={number}')
                if number >= 0:
                    cur.execute(f'DELETE FROM zad_vip WHERE id_akk={b[1]} and id_zad={number}')
                else:
                    cur.execute(f'DELETE FROM dop_vip WHERE id_akk={b[1]} and id_zad={number}')
                cur.execute(f'UPDATE akk SET raiting={b[0] - c} WHERE username="{a}"')
                base.commit()
                try:
                    if b[2] == 'ru':
                        await bot.send_message(b[1],
                                               text=f'Задание номер {number} не было зачтено, выполните его правильно чтобы получить баллы')
                    else:
                        await bot.send_message(b[1],
                                               text=f'Task number {number} was not counted, complete it correctly to get points')
                except Exception as e:
                    await message.answer('Сообщение не смогло отправиться человеку', reply_markup=keyboard_inline)
                    await state.finish()
                await message.answer('Задание успешно удалено', reply_markup=keyboard_inline)
                await state.finish()
            except Exception as e:
                await message.answer('Какая-то ошибка, попробуйте еще раз', reply_markup=keyboard_inline)
                await state.finish()
        else:
            await message.answer('Состояние сброшено', reply_markup=keyboard_inline)
            await state.finish()


# command admin
@dp.message_handler(commands='add_user')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        butomer1 = KeyboardButton(text="ru", callback_data=f"")
        butomer2 = KeyboardButton(text="en", callback_data=f"")
        keyboard_inline.add(butomer1, butomer2)
        keyboard_inline.insert(
            KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
        await message.answer('Введите язык предпочтительный для юзера ru или en\nПример: 7893464',
                             reply_markup=keyboard_inline)
        await FSMFriends.language.set()


@dp.message_handler(state=FSMFriends.language)
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        async with state.proxy() as data:
            data['language'] = message.text
        await message.answer('Введите id userа, которого хотите добавить\nПример: 7893464')
        await FSMFriends.id.set()


@dp.message_handler(state=FSMFriends.id)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        async with state.proxy() as data:
            data['id'] = message.text
        await message.answer('Введите username')
        await FSMFriends.next()


@dp.message_handler(state=FSMFriends.user)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            cur.execute(
                f'INSERT INTO akk(id_akk, raiting, username, language) VALUES ({data["id"]}, 0, "{message.text}", "{data["language"]}")')
            cur.execute(f'INSERT INTO parashut(id_akk, col) VALUES ({data["id"]}, 3)')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('User добавлен', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(commands='svodka')
async def register_friends_hourss(message: types.Message):
    if message.chat.id in admin_id:
        try:
            if message.text != '/svodka':
                c = message.text.split(" ")
                d = cur.execute(f'SELECT id_akk FROM zad_vip WHERE checker=0 and id_zad={int(c[1])}').fetchall()
                e = cur.execute(f'SELECT id_akk FROM zad_vip WHERE checker=1 and id_zad={int(c[1])}').fetchall()
                f = cur.execute(f'SELECT id_akk FROM akk').fetchall()
                await message.answer(f'По заданию {c[1]}\nПроверено: {len(e)}\nНе проверено: {len(d)}')
                await message.answer(
                    f'Не сделали: {len(f) - len(d) - len(e)}\nЧтобы посмотреть кто это введите /ne_sdali {c[1]}, где {c[1]} это номер задания')
            else:
                a = cur.execute(f'SELECT id_akk FROM zad_vip WHERE checker={0}').fetchall()
                b = cur.execute(f'SELECT id_akk FROM zad_vip WHERE checker={1}').fetchall()
                await message.answer(
                    f'Проверено: {len(b)}\nНе проверено: {len(a)}\nЕсли хотите посмотреть сводку по конкретному заданию введите /svodka 0, где 0 это номер задания')
        except Exception as e:
            await message.answer('Все задания проверены')


@dp.message_handler(commands='ne_sdali')
async def register_friends_hourss(message: types.Message):
    if message.chat.id in admin_id:
        try:
            if message.text != '/ne_sdali':
                c = message.text.split(" ")
                text = 'Не сдали:\n'
                d = [row[0] for row in cur.execute(f'SELECT id_akk FROM zad_vip WHERE id_zad={int(c[1])}').fetchall()]
                f = cur.execute(f'SELECT id_akk, username FROM akk').fetchall()
                for i in f:
                    if i[0] not in d:
                        text += f'{i[1]}\n'
                await message.answer(text)
            else:
                await message.answer(f'Введите как пример: /ne_sdali 2\nГде 2 это номер задания')
        except Exception as e:
            await message.answer('Все задания проверены')


@dp.message_handler(commands='help')
async def register_friends_hourss(message: types.Message):
    if message.chat.id in admin_id:
        await message.answer('Команды:\n/svodka\n/check_zadaniye\n/add_user')


@dp.message_handler(commands='check_zadaniye')
async def register_friends_hourss(message: types.Message):
    if message.chat.id in admin_id:
        try:
            a = cur.execute(f'SELECT id_akk,id_zad, description, video_id FROM zad_vip WHERE checker={0}').fetchone()
            b = cur.execute(f'SELECT username FROM akk WHERE id_akk={a[0]}').fetchone()
            text = f'{b[0]}\nЗадание:{a[1]}\nОписание:{a[2]}'
            await bot.send_message(message.chat.id, text=text)
            print(a[3])
            if a[3] != '-1000':
                if a[3].split('<>')[0] == 'photo':
                    try:
                        await bot.send_photo(message.chat.id, photo=a[3].split('<>')[1])
                    except Exception as e:
                        print(e)
                else:
                    try:
                        await bot.send_video(message.chat.id, video=a[3])
                    except Exception as e:
                        print(e)
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text=f"/check {a[0]} {a[1]} 0", callback_data=f"check_zadaniye")
            but3 = KeyboardButton(text=f"/check {a[0]} {a[1]} 5", callback_data=f"check_zadaniye")
            but4 = KeyboardButton(text=f"/cancel", callback_data=f"check_zadaniye")
            keyboard_inline.add(but2, but3, but4)
            await bot.send_message(message.chat.id, text=f'/check {a[0]} {a[1]} ball', reply_markup=keyboard_inline)
        except Exception as e:
            await message.answer('Все задания проверены')


@dp.message_handler(commands='check')
async def register_friends_hourss(message: types.Message):
    if message.chat.id in admin_id:
        try:
            a = message.text.split(" ")
            raiting = cur.execute(f'SELECT raiting FROM akk WHERE  id_akk=={int(a[1])}').fetchone()[0]
            cur.execute(f'UPDATE akk set raiting={raiting + int(a[3])} WHERE id_akk=={int(a[1])}')
            cur.execute(f'UPDATE zad_vip set checker=1 WHERE id_akk=={int(a[1])} and id_zad={int(a[2])}')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await bot.send_message(message.chat.id, text=f'Задание успешно проверено', reply_markup=keyboard_inline)
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(commands='add_zadaniye')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        butomer1 = KeyboardButton(text="ru", callback_data=f"")
        butomer2 = KeyboardButton(text="en", callback_data=f"")
        keyboard_inline.add(butomer1, butomer2)
        keyboard_inline.insert(
            KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
        await message.answer('Отправьте язык задания ru или en\nПример:ru', reply_markup=keyboard_inline)
        await FSMZadan.language.set()


@dp.message_handler(state=FSMZadan.language)
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        async with state.proxy() as data:
            data['language'] = message.text
        await message.answer('Отправьте номер задания\nПример:1')
        await FSMZadan.date.set()


# @dp.message_handler(state=FSMZadan.number)
# async def load_name(message: types.Message, state: FSMContext):
#     if message.chat.id in admin_id:
#         try:
#             async with state.proxy() as data:
#                 data['number'] = message.text
#             await message.answer('Отправьте дату задания\nПример:29.10.2022')
#             await FSMZadan.next()
#         except Exception as e:
#             await message.answer('Какая-то ошибка, попробуйте еще раз')
#             await state.finish()


@dp.message_handler(state=FSMZadan.date)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            async with state.proxy() as data:
                data['date'] = message.text
            await message.answer('Отправьте задание')
            await FSMZadan.text.set()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMZadan.text, content_types=['photo'])
async def get_message(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            file_id = 'photo^' + message.photo[-1].file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute('insert into zadaniya(number, name_video, description, date, language) values (?,?,?,?,?)', (int(data["date"]), file_id, kr, 111, data["language"]))
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Задание добавлено', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(state=FSMZadan.text, content_types=['video'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        # try:
        data = await state.get_data()
        file_id = message.video.file_id
        kr = ''
        if not (message.caption is None):
            kr = message.caption
        print(kr, int(data["date"]), file_id, data["language"])
        # base.execute(
        #     'CREATE TABLE IF NOT EXISTS zadaniya(id INTEGER PRIMARY KEY, number INTEGER, name_video varchar(20),'
        #     'description varvchar(20), language varvchar(20), date varchar(20))')
        # cur.execute(
        #     f'INSERT INTO zadaniya(number, name_video, description, date, language) VALUES({int(data["date"])}, "{file_id}", "{kr}", "{111}", "{data["language"]}")')
        cur.execute('insert into zadaniya(number, name_video, description, date, language) values (?,?,?,?,?)', (int(data["date"]), file_id, kr, 111, data["language"]))
        base.commit()
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
        but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
        but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
        but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
        but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
        but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
        but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
        but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
        but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
        but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
        but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
        but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
        but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
        keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13)
        keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
        await message.answer('Задание добавлено', reply_markup=keyboard_inline)
        await state.finish()
        # except Exception as e:
        #     print(e)
        #     await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(state=FSMZadan.text, content_types=['document'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            file_id = 'file^' + message.document.file_id
            print(file_id)
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute('insert into zadaniya(number, name_video, description, date, language) values (?,?,?,?,?)', (int(data["date"]), file_id, kr, 111, data["language"]))
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Задание добавлено', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            print(e)
            await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(state=FSMZadan.text, content_types=['text'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            cur.execute('insert into zadaniya(number, name_video, description, date, language) values (?,?,?,?,?)',
                        (int(data["date"]), "-1000", message.text, 111, data["language"]))
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Задание добавлено', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(commands='add_raiting')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        await message.answer('Введите username, которому хотите добавить баллов\nПример:@maks_afanasiev')
        await FSMRaiting.name.set()


@dp.message_handler(state=FSMRaiting.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            async with state.proxy() as data:
                data['name'] = message.text
            await message.answer(
                'Напишите сколько хотите добавить баллов\nПример:3\nЕсли хотите убавить напишите с минусом\nПример:-3')
            await FSMRaiting.next()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMRaiting.raiting)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            rt = data["name"]
            raiting = cur.execute(f'SELECT raiting FROM akk WHERE  username=="{rt}"').fetchone()[0]
            cur.execute(f'UPDATE akk set raiting={raiting + int(message.text)} WHERE username=="{rt}"')
            base.commit()
            await message.answer('Успешно обновлен рейтинг')
            await state.finish()
        except Exception as e:
            await message.answer('Человека нет в базе')
            await state.finish()


@dp.message_handler(commands='add_lesson')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
        butomer1 = KeyboardButton(text="ru", callback_data=f"")
        butomer2 = KeyboardButton(text="en", callback_data=f"")
        keyboard_inline.add(butomer1, butomer2)
        keyboard_inline.insert(
            KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
        await message.answer('Отправьте язык лекции ru или en\nПример:ru', reply_markup=keyboard_inline)
        await FSMLesson.language.set()


@dp.message_handler(state=FSMLesson.language)
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        async with state.proxy() as data:
            data['language'] = message.text
        await message.answer('Отправьте номер лекции\nПример:1')
        await FSMLesson.number.set()


@dp.message_handler(state=FSMLesson.number)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            async with state.proxy() as data:
                data['number'] = message.text
            await message.answer('Отправьте задание')
            await FSMLesson.text.set()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMLesson.text, content_types=['video'])
async def load_namer(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            file_id = message.video.file_id
            kr = ''
            if not (message.caption is None):
                kr = message.caption
            cur.execute(
                f'INSERT INTO lessons(number, name_video, description, language) VALUES ({int(data["number"])}, "{file_id}", "{kr}", "{data["language"]}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Лекция добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMLesson.text, content_types=['text'])
async def load_namer(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            data = await state.get_data()
            cur.execute(
                f'INSERT INTO lessons(number, name_video, description, language) VALUES ({int(data["number"])}, "{-1000}", "{message.text}", "{data["language"]}")')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = KeyboardButton(text="/check_zadaniye", callback_data=f"check_zadaniye")
            but10 = KeyboardButton(text="/add_user", callback_data=f"zadaniye_look")
            but1 = KeyboardButton(text="/add_raiting ", callback_data=f"zadaniye_look")
            but3 = KeyboardButton(text="/svodka", callback_data=f"zadaniye_lookppp")
            but4 = KeyboardButton(text="/ne_sdali", callback_data=f"zadaniye_lesson")
            but5 = KeyboardButton(text="/add_zadaniye", callback_data=f"zadaniye_lesson")
            but6 = KeyboardButton(text="/add_lesson", callback_data=f"zadaniyeeee_lesson")
            but7 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
            but8 = KeyboardButton(text="/add_pashalka", callback_data=f"zadaniyeeee_lesson")
            but9 = KeyboardButton(text="/check_pashalka", callback_data=f"zadaniyeeee_lesson")
            but11 = KeyboardButton(text="/add_instrukciya", callback_data=f"zadaniyeeee_lesson")
            but12 = KeyboardButton(text="/add_zagatovka", callback_data=f"zadaniyeeee_lesson")
            but13 = KeyboardButton(text="/drop_zadaniye", callback_data=f"zadaniyeeee_lesson")
            but14 = KeyboardButton(text="/check_people", callback_data=f"zadaniyeeee_lesson")
            keyboard_inline.add(but2, but10, but1, but6, but3, but4, but5, but7, but8, but9, but11, but12, but13, but14)
            keyboard_inline.insert(KeyboardButton(text="/cancel", callback_data=f"check_zadaniye"))
            await message.answer('Лекция добавлена', reply_markup=keyboard_inline)
            await state.finish()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.callback_query_handler(text_startswith="zad_dop")
async def start(call: CallbackQuery):
    if call.message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            number = call.data.split("_")[2]
            language = cur.execute(f'SELECT language FROM akk WHERE id_akk={call.message.chat.id}').fetchone()[0]
            hour = int(datetime.now(pytz.timezone('Europe/Moscow')).hour) + 6
            minute = int(datetime.now(pytz.timezone('Europe/Moscow')).minute)
            if language == "ru":
                a = cur.execute(f'SELECT name_video,description, date_hour, date_minute  FROM tek_zad_dop WHERE id_tek_zad={number} and language="ru"').fetchone()
                hour_now = hour - a[2]
                if a[3] < minute:
                    if hour == a[2] + 6:
                        minute_now = 60 - minute + a[3]
                        hour_now = hour_now - 1
                    else:
                        minute_now = 60 - minute + a[3]
                        hour_now = hour_now - 1
                else:
                    if a[3] != minute:
                        minute_now = a[3] - minute
                text = f'Пасхалочное задание {number}\nОставшееся время:{hour_now} часов {minute_now} минут\n'
            else:
                a = cur.execute(f'SELECT name_video,description, date_hour, date_minute  FROM tek_zad_dop WHERE id_tek_zad={number} and language="en"').fetchone()
                hour_now = hour - a[2]
                if a[3] < minute:
                    if hour == a[2] + 6:
                        minute_now = 60 - minute + a[3]
                        hour_now = hour_now - 1
                    else:
                        minute_now = 60 - minute + a[3]
                        hour_now = hour_now - 1
                else:
                    if a[3] != minute:
                        minute_now = a[3] - minute
                text = f'Easter task {number}\nRemaining time:{hour_now} hour {minute_now} minutes\n'
            if a[0] != '-1000':
                if a[0].split("^")[0] == 'photo':
                    await bot.send_photo(call.message.chat.id, photo=a[0].split("^")[1])
                else:
                    await bot.send_video(call.message.chat.id, video=a[0])
            if a[1] != '':
                text += a[1]
            await bot.send_message(call.message.chat.id, text=text)
        except Exception as e:
            await call.message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.callback_query_handler(text_startswith="zad_")
async def start(call: CallbackQuery):
    if call.message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            language = cur.execute(f'SELECT language FROM akk WHERE id_akk={call.message.chat.id}').fetchone()[0]
            number = call.data.split("_")[1]
            if language == "ru":
                text = f'Задание {number}\n'
            else:
                text = f'Task {number}\n'
            a = cur.execute(
                f'SELECT name_video,description  FROM zadaniya WHERE number={number} and language="{language}"').fetchone()
            if a[0] != '-1000':
                if a[0].split("^")[0] == 'photo':
                    await bot.send_photo(call.message.chat.id, photo=a[0].split("^")[1])
                else:
                    if a[0].split('^')[0] == 'file':
                        try:
                            await bot.send_document(channel_id, document=a[1].split('^')[1])
                        except Exception as e:
                            print(e)
                    else:
                        await bot.send_video(call.message.chat.id, video=a[0])
            if a[1] != '':
                text += a[1]
            await bot.send_message(call.message.chat.id, text=text)
        except Exception as e:
            await call.message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(text="Посмотреть задания")
async def start(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            # base.execute('CREATE TABLE IF NOT EXISTS zadaniya(id INTEGER PRIMARY KEY, number INTEGER, name_video varchar(20), '
            # 'description varvchar(20), date varchar(20))')
            # base.execute('CREATE TABLE IF NOT EXISTS akk(id INTEGER PRIMARY KEY, id_akk INTEGER, raiting INTEGER, username varchar(20))')
            # base.execute('CREATE TABLE IF NOT EXISTS zad_vip(id INTEGER PRIMARY KEY, id_akk INTEGER, id_zad INTEGER, id_message_id INTEGER)')

            a = [row[0] for row in cur.execute(f'SELECT number FROM zadaniya WHERE language="ru" ORDER BY number').fetchall()]
            b = [row[0] for row in
                 cur.execute(f'SELECT id_zad FROM zad_vip  WHERE id_akk={int(message.chat.id)}').fetchall()]
            keyboard_inline = InlineKeyboardMarkup(row_width=1)
            flag = 0
            flaggg = 0
            abt = 0
            try:
                print(dop_zad)
                abt = cur.execute(f'SELECT id_tek_zad FROM tek_zad_dop where id_tek_zad={dop_zad} and language="ru"').fetchone()[0]
                if abt < 0:
                    try:
                        if cur.execute(
                                f'SELECT id_akk FROM dop_vip WHERE id_zad={abt} and id_akk={int(message.chat.id)}').fetchone()[
                            0] == int(message.chat.id):
                            flaggg = 0
                        else:
                            flaggg = 1
                    except Exception as e:
                        flaggg = 1
            except Exception as e:
                print(e)
            if flaggg:
                keyboard_inline.insert(InlineKeyboardButton(text=f"Пасхалка", callback_data=f"zad_dop_{abt}"))
            for i in a:
                if i not in b:
                    if i == tek_zad:
                        keyboard_inline.insert(
                            InlineKeyboardButton(text=f"{i}(Задание на сегодня)", callback_data=f"zad_{i}"))
                    else:
                        keyboard_inline.insert(InlineKeyboardButton(text=f"{i}", callback_data=f"zad_{i}"))
                    flag = 1
            if flag or flaggg:
                await message.answer('Выберите задание,\nкоторое хотите посмотреть', reply_markup=keyboard_inline)
            else:
                await message.answer('Вы выполнили все задания на данный момент🥳')
        except Exception as e:
            await message.answer('Вы выполнили все задания на данный момент🥳')


@dp.message_handler(text="View tasks")
async def start(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            # base.execute('CREATE TABLE IF NOT EXISTS zadaniya(id INTEGER PRIMARY KEY, number INTEGER, name_video varchar(20), '
            # 'description varvchar(20), date varchar(20))')
            # base.execute('CREATE TABLE IF NOT EXISTS akk(id INTEGER PRIMARY KEY, id_akk INTEGER, raiting INTEGER, username varchar(20))')
            # base.execute('CREATE TABLE IF NOT EXISTS zad_vip(id INTEGER PRIMARY KEY, id_akk INTEGER, id_zad INTEGER, id_message_id INTEGER)')

            a = [row[0] for row in cur.execute(f'SELECT number FROM zadaniya WHERE language="en" ORDER BY number').fetchall()]
            b = [row[0] for row in
                 cur.execute(f'SELECT id_zad FROM zad_vip  WHERE id_akk={int(message.chat.id)}').fetchall()]
            keyboard_inline = InlineKeyboardMarkup(row_width=1)
            flag = 0
            flaggg = 0
            abt = 0
            try:
                abt = cur.execute(f'SELECT id_tek_zad FROM tek_zad_dop where id_tek_zad={dop_zad} and language="en"').fetchone()[0]
                if abt < 0:
                    try:
                        if cur.execute(
                                f'SELECT id_akk FROM dop_vip WHERE id_zad={abt} and id_akk={int(message.chat.id)}').fetchone()[
                            0] == int(message.chat.id):
                            flaggg = 0
                        else:
                            flaggg = 1
                    except Exception as e:
                        flaggg = 1
            except Exception as e:
                print(e)
            if flaggg:
                keyboard_inline.insert(InlineKeyboardButton(text=f"Easter Egg", callback_data=f"zad_dop_{abt}"))
            for i in a:
                if i not in b:
                    if i == tek_zad:
                        keyboard_inline.insert(
                            InlineKeyboardButton(text=f"{i}(The task for today)", callback_data=f"zad_{i}"))
                    else:
                        keyboard_inline.insert(InlineKeyboardButton(text=f"{i}", callback_data=f"zad_{i}"))
                    flag = 1
            if flag or flaggg:
                await message.answer('Select the task that you want to view', reply_markup=keyboard_inline)
            else:
                await message.answer('You have completed all the tasks so far🥳')
        except Exception as e:
            await message.answer('You have completed all the tasks so far🥳')


@dp.message_handler(text="Выполнить задание")
async def start(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but1 = KeyboardButton(text="Выполнить текущее задание", callback_data=f"zadaniye_vip")
            but2 = KeyboardButton(text="/cancel", callback_data=f"zadaniye_look")
            try:
                a = \
                    cur.execute(
                        f'SELECT id_zad FROM zad_vip  WHERE id_akk={int(message.chat.id)} and id_zad=0').fetchone()[
                        0]
                if a == 0:
                    keyboard_inline.add(but1, but2)
            except Exception as e:
                but3 = KeyboardButton(text="Выполнить нулевое задание", callback_data=f"zadaniye_vip")
                keyboard_inline.add(but3, but1, but2)
            flaggg = 0
            abt = 0
            try:
                abt = cur.execute(f'SELECT id_tek_zad FROM tek_zad_dop where id_tek_zad={dop_zad} and language="ru"').fetchone()[0]
                if abt < 0:
                    try:
                        if cur.execute(
                                f'SELECT id_akk FROM dop_vip WHERE id_zad={abt} and id_akk={int(message.chat.id)}').fetchone()[
                            0] == int(message.chat.id):
                            flaggg = 0
                        else:
                            flaggg = 1
                    except Exception as e:
                        flaggg = 1
            except Exception as e:
                print(e)
            if flaggg:
                keyboard_inline.add(KeyboardButton(text=f"Выполнить Пасхалку", callback_data=f"zad_dop_{abt}"))
            await message.answer(
                f'Напишите задание,которое хотите выполнить или нажмите Текущее задание для выполнения задания на сегодня или /cancel если не хотите выполнять сейчас\nТекуущее задание: {tek_zad}',
                reply_markup=keyboard_inline)
            await FSMZadanVip.name.set()
        except Exception as e:
            await message.answer('Какая-то неполадка, попробуйте зайти позже')


@dp.message_handler(text="Complete the task")
async def start(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            but1 = KeyboardButton(text="Complete the current task", callback_data=f"zadaniye_vip")
            but2 = KeyboardButton(text="/cancel", callback_data=f"zadaniye_look")
            try:
                a = \
                    cur.execute(
                        f'SELECT id_zad FROM zad_vip  WHERE id_akk={int(message.chat.id)} and id_zad=0').fetchone()[
                        0]
                if a == 0:
                    keyboard_inline.add(but1, but2)
            except Exception as e:
                but3 = KeyboardButton(text="Complete the zero task", callback_data=f"zadaniye_vip")
                keyboard_inline.add(but3, but1, but2)
            flaggg = 0
            abt = 0
            try:
                abt = cur.execute(f'SELECT id_tek_zad FROM tek_zad_dop where id_tek_zad={dop_zad} and language="en"').fetchone()[0]
                if abt < 0:
                    try:
                        if cur.execute(
                                f'SELECT id_akk FROM dop_vip WHERE id_zad={abt} and id_akk={int(message.chat.id)}').fetchone()[
                            0] == int(message.chat.id):
                            flaggg = 0
                        else:
                            flaggg = 1
                    except Exception as e:
                        flaggg = 1
            except Exception as e:
                print(e)
            if flaggg:
                keyboard_inline.add(KeyboardButton(text=f"Perform an Easter Egg", callback_data=f"zad_dop_{abt}"))
            await message.answer(
                f'Write the task you want to complete or click the Current task to complete the task for today or /cancel if you do not want to complete\nCurrent task now: {tek_zad}',
                reply_markup=keyboard_inline)
            await FSMZadanVip.name.set()
        except Exception as e:
            await message.answer('Какая-то неполадка, попробуйте зайти позже')


@dp.message_handler(state=FSMZadanVip.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        language = cur.execute(f'SELECT language FROM akk WHERE id_akk={message.chat.id}').fetchone()[0]
        if language == "ru":
            flagert = 0
            flaggg = 0
            abt = 0
            try:
                if tek_zad >= int(message.text):
                    rot = int(message.text)
                    flagert = 1
            except Exception as e:
                print(e)
            if message.text == 'Выполнить текущее задание':
                flagert = 1
                rot = tek_zad
            else:
                if message.text == "Выполнить нулевое задание":
                    flagert = 1
                    rot = 0
                else:
                    if message.text == "Выполнить Пасхалку":
                        flaggg = 0
                        try:
                            abt = cur.execute(f'SELECT id_tek_zad FROM tek_zad_dop where id_tek_zad={dop_zad} and language="ru"').fetchone()[0]
                            if abt < 0:
                                flaggg = 1
                        except Exception as e:
                            print(e)
                    else:
                        try:
                            rot = int(message.text)
                            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                            but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
                            but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
                            but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
                            but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
                            but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
                            but6 = KeyboardButton(text="Чат")
                            but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
                            but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
                            keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                            if tek_zad < int(message.text):
                                await message.answer(
                                    f'Такого нет задания,либо его выполнение ещё не наступило,сейчас актуально задание номер {tek_zad}, напишите его, либо закончите состояние нажав /cancel')
                                flagert = 0
                                await FSMZadanVip.name.set()
                        except Exception as e:
                            await message.answer('Необходимо ввести цифру задания либо нажать одну из кнопок')
                            flagert = 0
            if flagert:
                try:
                    a = [row[0] for row in cur.execute(f'SELECT number FROM zadaniya').fetchall()]
                    b = [row[0] for row in
                         cur.execute(f'SELECT id_zad FROM zad_vip  WHERE id_akk={int(message.chat.id)}').fetchall()]
                    if rot in a and rot not in b:
                        async with state.proxy() as data:
                            data['name'] = rot
                        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                        but2 = KeyboardButton(text="/cancel", callback_data=f"zadaniye_look")
                        keyboard_inline.add(but2)
                        try:
                            if cur.execute(
                                    f'SELECT id_akk FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[
                                0] == message.chat.id:
                                but3 = KeyboardButton(text="🪂", callback_data=f"zadaniye_lookeeer")
                                keyboard_inline.add(but3)
                        except Exception as e:
                            print(e)
                        await message.answer(
                            f'Вы выбрали задание: {rot}\nОтправьте ваш ответ в виде ссылки на историю или напишите /cancel для отмены действия',
                            reply_markup=keyboard_inline)
                        await FSMZadanVip.file.set()
                    else:
                        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                        but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
                        but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
                        but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
                        but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
                        but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
                        but6 = KeyboardButton(text="Чат")
                        but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
                        but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
                        keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                        await message.answer('Данное задание либо еще не вышло, либо вы его уже выполнили',
                                             reply_markup=keyboard_inline)
                        await state.finish()
                except Exception as e:
                    keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                    but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
                    but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
                    but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
                    but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
                    but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
                    but6 = KeyboardButton(text="Чат")
                    but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
                    but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
                    keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                    await message.answer('Какая-то ошибка, попробуйте позже', reply_markup=keyboard_inline)
                    await state.finish()
            if flaggg:
                try:
                    b = [row[0] for row in
                         cur.execute(f'SELECT id_zad FROM zad_vip  WHERE id_akk={int(message.chat.id)}').fetchall()]
                    if abt not in b:
                        async with state.proxy() as data:
                            data['name'] = abt
                        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                        but2 = KeyboardButton(text="/cancel", callback_data=f"zadaniye_look")
                        keyboard_inline.add(but2)
                        try:
                            if cur.execute(
                                    f'SELECT id_akk FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[
                                0] == message.chat.id:
                                cocl = cur.execute(
                                    f'SELECT col FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[0]
                                but3 = KeyboardButton(text=f"🪂", callback_data=f"zadaniye_lookeeer")
                                keyboard_inline.add(but3)
                        except Exception as e:
                            print(e)
                        await message.answer(
                            f'Вы выбрали текущую пасхалку\nОтправьте ваш ответ в виде ссылки на историю или напишите /cancel для отмены действия',
                            reply_markup=keyboard_inline)
                        await FSMZadanVip.file.set()
                    else:
                        await message.answer('Данное задание либо еще не вышло, либо вы его уже выполнили',
                                             reply_markup=keyboard_inline)
                        await state.finish()
                except Exception as e:
                    keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                    but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
                    but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
                    but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
                    but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
                    but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
                    but6 = KeyboardButton(text="Чат")
                    but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
                    but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
                    keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                    await message.answer('Какая-то ошибка, попробуйте позже', reply_markup=keyboard_inline)
                    await state.finish()
        else:
            flagert = 0
            flaggg = 0
            abt = 0
            try:
                if tek_zad >= int(message.text):
                    rot = int(message.text)
                    flagert = 1
            except Exception as e:
                print(e)
            if message.text == 'Complete the current task':
                flagert = 1
                rot = tek_zad
            else:
                if message.text == "Complete the zero task":
                    flagert = 1
                    rot = 0
                else:
                    if message.text == "Perform an Easter Egg":
                        flaggg = 0
                        try:
                            abt = cur.execute(f'SELECT id_tek_zad FROM tek_zad_dop where id_tek_zad={dop_zad} and language="ru"').fetchone()[0]
                            if abt < 0:
                                flaggg = 1
                        except Exception as e:
                            print(e)
                    else:
                        try:
                            rot = int(message.text)
                            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                            but1 = KeyboardButton(text="Complete the task", callback_data=f"zadaniye_vip")
                            but2 = KeyboardButton(text="View tasks", callback_data=f"zadaniye_look")
                            but3 = KeyboardButton(text="View the rating", callback_data=f"zadaniye_lookppp")
                            but4 = KeyboardButton(text="Lessons", callback_data=f"zadaniye_lesson")
                            but5 = KeyboardButton(text="Instruction", callback_data=f"zadaniye_lesson")
                            but6 = KeyboardButton(text="Chat")
                            but7 = KeyboardButton(text="Change the language", callback_data=f"zadaniye_lesson")
                            but8 = KeyboardButton(text="Blanks", callback_data=f"zadaniye_lesson")
                            keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                            if tek_zad < int(message.text):
                                await message.answer(
                                    f'There is no such task, or its completion has not yet come, now the task number is relevant {tek_zad}, write it, or finish the state by clicking /cancel')
                                flagert = 0
                                await FSMZadanVip.name.set()
                        except Exception as e:
                            await message.answer('You must enter the number of the task or press one of the buttons')
                            flagert = 0
            if flagert:
                try:
                    a = [row[0] for row in cur.execute(f'SELECT number FROM zadaniya').fetchall()]
                    b = [row[0] for row in
                         cur.execute(f'SELECT id_zad FROM zad_vip  WHERE id_akk={int(message.chat.id)}').fetchall()]
                    if rot in a and rot not in b:
                        async with state.proxy() as data:
                            data['name'] = rot
                        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                        but2 = KeyboardButton(text="/cancel", callback_data=f"zadaniye_look")
                        keyboard_inline.add(but2)
                        try:
                            if cur.execute(
                                    f'SELECT id_akk FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[
                                0] == message.chat.id:
                                but3 = KeyboardButton(text="🪂", callback_data=f"zadaniye_lookeeer")
                                keyboard_inline.add(but3)
                        except Exception as e:
                            print(e)
                        await message.answer(
                            f'You have chosen a task: {rot}\nSend your response in the form of a link to the story, or write /cancel to cancel an action',
                            reply_markup=keyboard_inline)
                        await FSMZadanVip.file.set()
                    else:
                        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                        but1 = KeyboardButton(text="Complete the task", callback_data=f"zadaniye_vip")
                        but2 = KeyboardButton(text="View tasks", callback_data=f"zadaniye_look")
                        but3 = KeyboardButton(text="View the rating", callback_data=f"zadaniye_lookppp")
                        but4 = KeyboardButton(text="Lessons", callback_data=f"zadaniye_lesson")
                        but5 = KeyboardButton(text="Instruction", callback_data=f"zadaniye_lesson")
                        but6 = KeyboardButton(text="Chat")
                        but7 = KeyboardButton(text="Change the language", callback_data=f"zadaniye_lesson")
                        but8 = KeyboardButton(text="Blanks", callback_data=f"zadaniye_lesson")
                        keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                        await message.answer(
                            'This task has either not been completed yet, or you have already completed it',
                            reply_markup=keyboard_inline)
                        await state.finish()
                except Exception as e:
                    keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                    but1 = KeyboardButton(text="Complete the task", callback_data=f"zadaniye_vip")
                    but2 = KeyboardButton(text="View tasks", callback_data=f"zadaniye_look")
                    but3 = KeyboardButton(text="View the rating", callback_data=f"zadaniye_lookppp")
                    but4 = KeyboardButton(text="Lessons", callback_data=f"zadaniye_lesson")
                    but5 = KeyboardButton(text="Instruction", callback_data=f"zadaniye_lesson")
                    but6 = KeyboardButton(text="Chat")
                    but7 = KeyboardButton(text="Change the language", callback_data=f"zadaniye_lesson")
                    but8 = KeyboardButton(text="Blanks", callback_data=f"zadaniye_lesson")
                    keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                    await message.answer('Some kind of mistake, try again later', reply_markup=keyboard_inline)
                    await state.finish()
            if flaggg:
                try:
                    b = [row[0] for row in
                         cur.execute(f'SELECT id_zad FROM zad_vip  WHERE id_akk={int(message.chat.id)}').fetchall()]
                    if abt not in b:
                        async with state.proxy() as data:
                            data['name'] = abt
                        keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                        but2 = KeyboardButton(text="/cancel", callback_data=f"zadaniye_look")
                        keyboard_inline.add(but2)
                        try:
                            if cur.execute(
                                    f'SELECT id_akk FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[
                                0] == message.chat.id:
                                cocl = cur.execute(
                                    f'SELECT col FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[0]
                                but3 = KeyboardButton(text=f"🪂", callback_data=f"zadaniye_lookeeer")
                                keyboard_inline.add(but3)
                        except Exception as e:
                            print(e)
                        await message.answer(
                            f'You have chosen the current Easter egg\nSend your response in the form of a link to the story, or write /cancel to cancel the action',
                            reply_markup=keyboard_inline)
                        await FSMZadanVip.file.set()
                    else:
                        await message.answer(
                            'This task has either not been completed yet, or you have already completed it',
                            reply_markup=keyboard_inline)
                        await state.finish()
                except Exception as e:
                    keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                    but1 = KeyboardButton(text="Complete the task", callback_data=f"zadaniye_vip")
                    but2 = KeyboardButton(text="View tasks", callback_data=f"zadaniye_look")
                    but3 = KeyboardButton(text="View the rating", callback_data=f"zadaniye_lookppp")
                    but4 = KeyboardButton(text="Lessons", callback_data=f"zadaniye_lesson")
                    but5 = KeyboardButton(text="Instruction", callback_data=f"zadaniye_lesson")
                    but6 = KeyboardButton(text="Chat")
                    but7 = KeyboardButton(text="Change the language", callback_data=f"zadaniye_lesson")
                    but8 = KeyboardButton(text="Blanks", callback_data=f"zadaniye_lesson")
                    keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                    await message.answer('Какая-то ошибка, попробуйте позже', reply_markup=keyboard_inline)
                    await state.finish()


#@dp.message_handler(state=FSMZadanVip.file, content_types=['photo'])
#async def get_message(message: types.Message, state: FSMContext):
#    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
#        try:
#            file_id = 'photo<>' + message.photo[-1].file_id
#            kr = ''
#            if not (message.text is None):
#                kr = message.text
#            if not (message.caption is None):
#                kr += message.caption
#            async with state.proxy() as data:
#                data['file'] = f'{kr}^{file_id}'
#            language = cur.execute(f'SELECT language FROM akk WHERE id_akk={message.chat.id}').fetchone()[0]
#            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
#            if language == "ru":
#                but1 = KeyboardButton(text="Да", callback_data=f"zadaniye_vip")
#                but2 = KeyboardButton(text="Нет", callback_data=f"zadaniye_look")
#                keyboard_inline.add(but1, but2)
#                await message.answer('Вы точно хотите отправить это сообщение как задание?\n',
#                                     reply_markup=keyboard_inline)
#            else:
#                buter1 = KeyboardButton(text="Yes", callback_data=f"zadaniye_vip")
#                buter2 = KeyboardButton(text="No", callback_data=f"zadaniye_look")
#                keyboard_inline.add(buter1, buter2)
#                await message.answer('Are you sure you want to send this message as a task?\n',
#                                     reply_markup=keyboard_inline)
#            await FSMZadanVip.id.set()
#        except Exception as e:
#            await message.answer('Какая-то ошибка, попробуйте еще раз')
#            await state.finish()


#@dp.message_handler(state=FSMZadanVip.file, content_types=['video'])
#async def load_name(message: types.Message, state: FSMContext):
#    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
#        try:
#            file_id = message.video.file_id
#            kr = ''
#            if not (message.text is None):
#                kr = message.text
#            if not (message.caption is None):
#                kr += message.caption
#            async with state.proxy() as data:
#                data['file'] = f'{kr}^{file_id}'
#            language = cur.execute(f'SELECT language FROM akk WHERE id_akk={message.chat.id}').fetchone()[0]
#            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
#            if language == "ru":
#                but1 = KeyboardButton(text="Да", callback_data=f"zadaniye_vip")
#                but2 = KeyboardButton(text="Нет", callback_data=f"zadaniye_look")
#                keyboard_inline.add(but1, but2)
#                await message.answer('Вы точно хотите отправить это сообщение как задание?\n',
#                                     reply_markup=keyboard_inline)
#            else:
#                buter1 = KeyboardButton(text="Yes", callback_data=f"zadaniye_vip")
#                buter2 = KeyboardButton(text="No", callback_data=f"zadaniye_look")
#                keyboard_inline.add(buter1, buter2)
#                await message.answer('Are you sure you want to send this message as a task?\n',
#                                     reply_markup=keyboard_inline)
#            await FSMZadanVip.id.set()
#        except Exception as e:
#            await message.answer('Какая-то ошибка, попробуйте еще раз')
#            await state.finish()


@dp.message_handler(state=FSMZadanVip.file, content_types=['text'])
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            if message.text in quer:
                keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
                but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
                but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
                but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
                but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
                but6 = KeyboardButton(text="Чат")
                but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
                but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
                keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                await message.answer('Это не является ответом на задание', reply_markup=keyboard_inline)
                await state.finish()
            else:
                kr = ''
                if not (message.text is None):
                    kr = message.text
                if not (message.caption is None):
                    kr += message.caption
                async with state.proxy() as data:
                    data['file'] = kr
                language = cur.execute(f'SELECT language FROM akk WHERE id_akk={message.chat.id}').fetchone()[0]
                keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
                if language == "ru":
                    but1 = KeyboardButton(text="Да", callback_data=f"zadaniye_vip")
                    but2 = KeyboardButton(text="Нет", callback_data=f"zadaniye_look")
                    keyboard_inline.add(but1, but2)
                    texter = 'Вы точно хотите отправить это сообщение как задание?\n'
                else:
                    buter1 = KeyboardButton(text="Yes", callback_data=f"zadaniye_vip")
                    buter2 = KeyboardButton(text="No", callback_data=f"zadaniye_look")
                    keyboard_inline.add(buter1, buter2)
                    texter = 'Are you sure you want to send this message as a task?\n'
                if message.text == '🪂':
                    try:
                        if language == "ru":
                            if cur.execute(
                                    f'SELECT id_akk FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[
                                0] == message.chat.id:
                                cocl = cur.execute(
                                    f'SELECT col FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[0]
                                await message.answer(
                                    f'Вы точно хотите использовать парашют?\nУ вас осталось {cocl} парашюта\nПарашют это ваш помощник. Если вы куда-то уехали, а задание выполнить надо, то вы можете воспользоваться парашютом и пропустить задание. Всего у вас есть 3 парашюта за весь марафон, используйте с умом)',
                                    reply_markup=keyboard_inline)
                            else:
                                await message.answer('Вы не можете использовать парашют\n')
                                await state.finish()
                        else:
                            if cur.execute(
                                    f'SELECT id_akk FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[
                                0] == message.chat.id:
                                cocl = cur.execute(
                                    f'SELECT col FROM parashut where id_akk=={message.chat.id} and col>0').fetchone()[0]
                                await message.answer(
                                    f'Are you sure you want to use a parachute?\nYou have {cocl} parachute\nThe parachute is your assistant. If you have gone somewhere and the task needs to be completed, then you can use a parachute and skip the task. In total, you have 3 parachutes for the entire marathon, use them wisely)',
                                    reply_markup=keyboard_inline)
                            else:
                                await message.answer('You can not use a parachute\n')
                                await state.finish()
                    except Exception as e:
                        print(e)
                else:
                    await message.answer(texter, reply_markup=keyboard_inline)
                await FSMZadanVip.id.set()
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')
            await state.finish()


@dp.message_handler(state=FSMZadanVip.id)
async def load_name(message: types.Message, state: FSMContext):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            tz_NY = pytz.timezone('Asia/Dubai')
            d_NY = datetime.now(tz_NY).hour
            language = cur.execute(f'SELECT language FROM akk WHERE id_akk={message.chat.id}').fetchone()[0]
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            if language == "ru":
                but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
                but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
                but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
                but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
                but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
                but6 = KeyboardButton(text="Чат")
                but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
                but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
                keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                if message.text == 'Да':
                    data = await state.get_data()
                    if data["file"] == '🪂':
                        try:
                            coler = cur.execute(f'SELECT col FROM parashut where id_akk=={message.chat.id}').fetchone()[
                                0]
                            cur.execute(f'UPDATE parashut set col={coler - 1} WHERE id_akk=={int(message.chat.id)}')
                            base.commit()
                        except Exception as e:
                            print(e)
                    if int(data["name"]) < 0:
                        rait = 50
                        a = data["file"].split("^")
                        if len(a) > 1:
                            ry = a[0]
                            ru = a[1]
                        else:
                            ry = a[0]
                            ru = -1000
                        cur.execute(
                            f'INSERT INTO dop_vip(id_akk, id_zad, description, video_id, checker) VALUES ({int(message.chat.id)},{int(data["name"])}, "{ry}", "{ru}", 0)')
                        raiting = \
                        cur.execute(f'SELECT raiting FROM akk WHERE  id_akk=={int(message.chat.id)}').fetchone()[
                            0]
                        cur.execute(f'UPDATE akk set raiting={raiting + rait} WHERE id_akk=={int(message.chat.id)}')
                        base.commit()
                        try:
                            rty = \
                            cur.execute(f'SELECT username FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()[0]
                            cur.execute(
                                f'INSERT INTO drop_zad(id_akk, id_zad, username, ball) VALUES({message.chat.id}, {int(data["name"])}, "{rty}", {rait})')
                            base.commit()
                        except Exception as e:
                            print(e)
                        await message.answer('Задание отправлено и будет проверено🔥', reply_markup=keyboard_inline)
                        b = cur.execute(f'SELECT username FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()
                        text = f'{b[0]}\nПасхалка\nОписание:{ry}'
                        if len(a) > 1:
                            if a[1].split('<>')[0] == 'photo':
                                try:
                                    await bot.send_photo(channel_id, photo=a[1].split('<>')[1])
                                except Exception as e:
                                    print(e)
                            else:
                                try:
                                    await bot.send_video(channel_id, video=ru)
                                except Exception as e:
                                    print(e)
                        try:
                            await bot.send_message(channel_id, text=text)
                        except Exception as e:
                            print(e)
                        await state.finish()
                    else:
                        rait = 5
                        if tek_zad == int(data["name"]):
                            rait = 5
                            if 14 >= d_NY >= 4:
                                rait += 15
                            else:
                                if 16 >= d_NY >= 4:
                                    rait += 10
                                else:
                                    if 18 >= d_NY >= 4:
                                        rait += 5
                        if int(data["name"]) == 0:
                            rait = 20
                        a = data["file"].split("^")
                        if len(a) > 1:
                            ry = a[0]
                            ru = a[1]
                        else:
                            ry = a[0]
                            ru = -1000
                        cur.execute(
                            f'INSERT INTO zad_vip(id_akk, id_zad, description, video_id, checker) VALUES ({int(message.chat.id)},{int(data["name"])}, "{ry}", "{ru}", 0)')
                        raiting = \
                        cur.execute(f'SELECT raiting FROM akk WHERE  id_akk=={int(message.chat.id)}').fetchone()[
                            0]
                        cur.execute(f'UPDATE akk set raiting={raiting + rait} WHERE id_akk=={int(message.chat.id)}')
                        base.commit()
                        try:
                            rty = \
                            cur.execute(f'SELECT username FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()[0]
                            cur.execute(
                                f'INSERT INTO drop_zad(id_akk, id_zad, username, ball) VALUES({message.chat.id}, {int(data["name"])}, "{rty}", {rait})')
                            base.commit()
                        except Exception as e:
                            print(e)
                        await message.answer('Задание отправлено и будет проверено🔥', reply_markup=keyboard_inline)
                        b = cur.execute(f'SELECT username FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()
                        text = f'{b[0]}\nЗадание:{int(data["name"])}\nОписание:{ry}'
                        if len(a) > 1:
                            if a[1].split('<>')[0] == 'photo':
                                try:
                                    await bot.send_photo(channel_id, photo=a[1].split('<>')[1])
                                except Exception as e:
                                    print(e)
                            else:
                                try:
                                    await bot.send_video(channel_id, video=ru)
                                except Exception as e:
                                    print(e)
                        try:
                            await bot.send_message(channel_id, text=text)
                        except Exception as e:
                            print(e)
                        await state.finish()
                else:
                    await message.answer('Ответ на задание отменен', reply_markup=keyboard_inline)
                    await state.finish()
            else:
                but1 = KeyboardButton(text="Complete the task", callback_data=f"zadaniye_vip")
                but2 = KeyboardButton(text="View tasks", callback_data=f"zadaniye_look")
                but3 = KeyboardButton(text="View the rating", callback_data=f"zadaniye_lookppp")
                but4 = KeyboardButton(text="Lessons", callback_data=f"zadaniye_lesson")
                but5 = KeyboardButton(text="Instruction", callback_data=f"zadaniye_lesson")
                but6 = KeyboardButton(text="Chat")
                but7 = KeyboardButton(text="Change the language", callback_data=f"zadaniye_lesson")
                but8 = KeyboardButton(text="Blanks", callback_data=f"zadaniye_lesson")
                keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                if message.text == 'Yes':
                    data = await state.get_data()
                    if data["file"] == '🪂':
                        try:
                            coler = cur.execute(f'SELECT col FROM parashut where id_akk=={message.chat.id}').fetchone()[
                                0]
                            cur.execute(f'UPDATE parashut set col={coler - 1} WHERE id_akk=={int(message.chat.id)}')
                            base.commit()
                        except Exception as e:
                            print(e)
                    if int(data["name"]) < 0:
                        rait = 50
                        a = data["file"].split("^")
                        if len(a) > 1:
                            ry = a[0]
                            ru = a[1]
                        else:
                            ry = a[0]
                            ru = -1000
                        cur.execute(
                            f'INSERT INTO dop_vip(id_akk, id_zad, description, video_id, checker) VALUES ({int(message.chat.id)},{int(data["name"])}, "{ry}", "{ru}", 0)')
                        raiting = \
                            cur.execute(f'SELECT raiting FROM akk WHERE  id_akk=={int(message.chat.id)}').fetchone()[
                                0]
                        cur.execute(f'UPDATE akk set raiting={raiting + rait} WHERE id_akk=={int(message.chat.id)}')
                        base.commit()
                        try:
                            rty = \
                            cur.execute(f'SELECT username FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()[0]
                            cur.execute(
                                f'INSERT INTO drop_zad(id_akk, id_zad, username, ball) VALUES({message.chat.id}, {int(data["name"])}, "{rty}", {rait})')
                            base.commit()
                        except Exception as e:
                            print(e)
                        await message.answer('The task has been submitted and will be verified🔥',
                                             reply_markup=keyboard_inline)
                        b = cur.execute(f'SELECT username FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()
                        text = f'{b[0]}\nEaster Egg\nDescription:{ry}'
                        if len(a) > 1:
                            if a[1].split('<>')[0] == 'photo':
                                try:
                                    await bot.send_photo(channel_id, photo=a[1].split('<>')[1])
                                except Exception as e:
                                    print(e)
                            else:
                                try:
                                    await bot.send_video(channel_id, video=ru)
                                except Exception as e:
                                    print(e)
                        try:
                            await bot.send_message(channel_id, text=text)
                        except Exception as e:
                            print(e)
                        await state.finish()
                    else:
                        rait = 5
                        if tek_zad == int(data["name"]):
                            rait = 5
                            if 14 >= d_NY >= 4:
                                rait += 15
                            else:
                                if 16 >= d_NY >= 4:
                                    rait += 10
                                else:
                                    if 18 >= d_NY >= 4:
                                        rait += 5
                        if int(data["name"]) == 0:
                            rait = 20
                        a = data["file"].split("^")
                        if len(a) > 1:
                            ry = a[0]
                            ru = a[1]
                        else:
                            ry = a[0]
                            ru = -1000
                        cur.execute(
                            f'INSERT INTO zad_vip(id_akk, id_zad, description, video_id, checker) VALUES ({int(message.chat.id)},{int(data["name"])}, "{ry}", "{ru}", 0)')
                        raiting = \
                            cur.execute(f'SELECT raiting FROM akk WHERE  id_akk=={int(message.chat.id)}').fetchone()[
                                0]
                        cur.execute(f'UPDATE akk set raiting={raiting + rait} WHERE id_akk=={int(message.chat.id)}')
                        base.commit()
                        try:
                            rty = cur.execute(f'SELECT username FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()[0]
                            cur.execute(
                                f'INSERT INTO drop_zad(id_akk, id_zad, username, ball) VALUES({message.chat.id}, {int(data["name"])}, "{rty}", {rait})')
                            base.commit()
                        except Exception as e:
                            print(e)
                        await message.answer('The task has been submitted and will be verified🔥',
                                             reply_markup=keyboard_inline)
                        b = cur.execute(f'SELECT username FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()
                        text = f'{b[0]}\nTask:{int(data["name"])}\nDescription:{ry}'
                        if len(a) > 1:
                            if a[1].split('<>')[0] == 'photo':
                                try:
                                    await bot.send_photo(channel_id, photo=a[1].split('<>')[1])
                                except Exception as e:
                                    print(e)
                            else:
                                try:
                                    await bot.send_video(channel_id, video=ru)
                                except Exception as e:
                                    print(e)
                        try:
                            await bot.send_message(channel_id, text=text)
                        except Exception as e:
                            print(e)
                        await state.finish()
                else:
                    await message.answer('The response to the task has been canceled', reply_markup=keyboard_inline)
                    await state.finish()
        except Exception as e:
            await message.answer('Some kind of mistake, try again')
            await state.finish()


@dp.message_handler(text='Посмотреть рейтинг')
async def start(message: types.Message):
    try:
        a = cur.execute(f'SELECT raiting,username FROM akk ORDER BY raiting DESC LIMIT 50').fetchall()
        rt = cur.execute(f'SELECT COUNT(*) FROM akk').fetchone()[0]
        rtb = cur.execute(f'SELECT COUNT(*) FROM akk WHERE raiting>0').fetchone()[0]
        b = int(len(a))
        if not (int(len(a)) is int):
            b = int(len(a))
        text = f'Топ игроков:\n________Топ 10________\n'
        for i in range(b):
            if i==10:
                text += '______________________\n'
            text += f'{a[i][1]} - {a[i][0]}\n'
        text += f'Всего участников: {rt}\nСтартовали в марафоне: {rtb}'
        await message.answer(text)
        if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
            a = cur.execute(f'SELECT raiting FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()
            await message.answer(f'Your rating: {a[0]}')
    except Exception as e:
        await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(text='View the rating')
async def start(message: types.Message):
    try:
        a = cur.execute(f'SELECT raiting,username FROM akk ORDER BY raiting DESC LIMIT 50').fetchall()
        rt = cur.execute(f'SELECT COUNT(*) FROM akk').fetchone()[0]
        rtb = cur.execute(f'SELECT COUNT(*) FROM akk WHERE raiting>0').fetchone()[0]
        b = int(len(a))
        if not (int(len(a)) is int):
            b = int(len(a))
        text = f'Top Players:\n'
        for i in range(b):
            text += f'{a[i][1]} - {a[i][0]}\n'
        text += f'Всего участников: {rt}\nThose who started the marathon: {rtb}'
        await message.answer(text)
        if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
            a = cur.execute(f'SELECT raiting FROM akk WHERE id_akk={int(message.chat.id)}').fetchone()
            await message.answer(f'Your rating: {a[0]}')
    except Exception as e:
        await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(text='Чат')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        await message.answer('Наш чат, подключайся)\nhttps://t.me/Laika_storis')


@dp.message_handler(text='Chat')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        await message.answer('Our chat, connect)\nhttps://t.me/Laika_storis')


@dp.message_handler(text='Инструкция')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        # but1 = InlineKeyboardButton(text="Как установить premium аккаунт в Telegram", callback_data=f"zadaniyetrainer3")
        # but2 = InlineKeyboardButton(text="Как добавить субтитры в видео",
        #                             callback_data=f"zadaniyetrainer4")
        keyboard_inline1 = InlineKeyboardMarkup(row_width=1)
        # keyboard_inline1.add(but2)
        # try:
        a = cur.execute('SELECT name, id from  instruct where language="ru"').fetchall()
        for i in a:
            keyboard_inline1.insert(InlineKeyboardButton(text=f"{i[0]}", callback_data=f"zadaniyetrainer_{i[1]}"))
        # except Exception as e:
        #     await message.answer('Какая-то ошибка, попробуйте еще раз')
        await message.answer('Инструкция', reply_markup=keyboard_inline1)
    if message.chat.id in admin_id:
        await message.answer('''/add_user - добавить пользвателя\n
/svodka - сводка по проверенным и непроверенным заданиям
(/svodka 0 - сводка по проверенным, непроверенным работам по заданию в данном случае 0, а также выводит кол-во должников\n
/ne_sdali 0 - выводит никнеймы участников, которые не сдали задание в данном случае 0\n
/check_zadaniye - запускает цикличную проверку заданий вами, вы просматриваете каждое задание и проставляете баллы, если устали и хотите закончить нажмите /cancel и машина выйдет из состояния проверки\n
/add_zadaniye и /add_lesson - это функции для добавления заданий и уроков, также если вы где-то не то ввели или просто хотите прекратить это действие, отправьте /cancel
/add_raiting - команда увеличения или уменьшения рейтинга участника
/add_pashalka - добавить пасхалку
/check_pashalka - проверить пасхалки
/add_instrukciya - добавить инструкцию''')


@dp.message_handler(text='Заготовки')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        keyboard_inline1 = InlineKeyboardMarkup(row_width=1)
        try:
            a = cur.execute('SELECT name, id from  zagatovka where language="ru"').fetchall()
            if a:
                for i in a:
                    keyboard_inline1.insert(InlineKeyboardButton(text=f"{i[0]}", callback_data=f"zadantran_{i[1]}"))
                await message.answer('Заготовки', reply_markup=keyboard_inline1)
            else:
                await message.answer('Заготовок пока нет')
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(text='Blanks')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        keyboard_inline1 = InlineKeyboardMarkup(row_width=1)
        try:
            a = cur.execute('SELECT name, id from  zagatovka where language="en"').fetchall()
            if a:
                for i in a:
                    keyboard_inline1.insert(InlineKeyboardButton(text=f"{i[0]}", callback_data=f"zadantran_{i[1]}"))
                await message.answer('Blanks', reply_markup=keyboard_inline1)
            else:
                await message.answer('No blanks yet')
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(text='Instruction')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        # but1 = InlineKeyboardButton(text="Как установить premium аккаунт в Telegram", callback_data=f"zadaniyetrainer3")
        # but2 = InlineKeyboardButton(text="Как добавить субтитры в видео",
        #                             callback_data=f"zadaniyetrainer4")
        keyboard_inline1 = InlineKeyboardMarkup(row_width=1)
        # keyboard_inline1.add(but2)
        # try:
        a = cur.execute('SELECT name, id from  instruct where language="en"').fetchall()
        for i in a:
            keyboard_inline1.insert(InlineKeyboardButton(text=f"{i[0]}", callback_data=f"zadaniyetrainer_{i[1]}"))
        # except Exception as e:
        #     await message.answer('Какая-то ошибка, попробуйте еще раз')
        await message.answer('Instruction', reply_markup=keyboard_inline1)


@dp.message_handler(text='Уроки')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            a = [row[0] for row in cur.execute(f'SELECT number FROM lessons WHERE language="ru"').fetchall()]
            if len(a) == 0:
                await message.answer('Пока что нет уроков')
            else:
                keyboard_inline = InlineKeyboardMarkup(row_width=1)
                for i in a:
                    keyboard_inline.insert(InlineKeyboardButton(text=f"{i}", callback_data=f"les_{i}_ru"))
                await message.answer('Выберите урок,\nкоторый хотите посмотреть', reply_markup=keyboard_inline)
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(text='Lessons')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            a = [row[0] for row in cur.execute(f'SELECT number FROM lessons WHERE language="en"').fetchall()]
            if len(a) == 0:
                await message.answer('There are no lessons yet')
            else:
                keyboard_inline = InlineKeyboardMarkup(row_width=1)
                for i in a:
                    keyboard_inline.insert(InlineKeyboardButton(text=f"{i}", callback_data=f"les_{i}_en"))
                await message.answer('Choose a lesson,\nwhich one do you want to watch', reply_markup=keyboard_inline)
        except Exception as e:
            await message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.callback_query_handler(text_startswith="les_")
async def start(call: CallbackQuery):
    if call.message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            rut = call.data.split("_")
            number = rut[1]
            lan = rut[2]
            a = cur.execute(
                f'SELECT name_video,description  FROM lessons WHERE number={number} and language="{lan}"').fetchone()
            if lan == "ru":
                text = f'Урок {number}\n'
            else:
                text = f'Lesson {number}\n'
            if a[0] != '-1000':
                await bot.send_video(call.message.chat.id, video=a[0])
            if a[1] != '':
                text += a[1]
            await bot.send_message(call.message.chat.id, text=text)
        except Exception as e:
            await call.message.answer('Какая-то ошибка, попробуйте еще раз')


# @dp.callback_query_handler(text='zadaniyetrainer3')
# async def load_name(call: CallbackQuery):
#     if call.message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
#         await bot.send_video(call.message.chat.id, video=video_tg_premiun, caption=text_tg_premiun)


@dp.callback_query_handler(text='zadaniyetrainer4')
async def load_name(call: CallbackQuery):
    if call.message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        await bot.send_video(call.message.chat.id, video=video_tg_premiun1, caption=text_tg_premiun1)


@dp.callback_query_handler(text_startswith='zadaniyetrainer1_')
async def load_name(call: CallbackQuery):
    number = call.data.split("_")[1]
    if number == "en":
        await bot.send_document(call.message.chat.id, document=pdf_file_en)
        await bot.send_message(call.message.chat.id,
                               'Hello dear visitor, you can find out more about our marathon in the presentation or by following the link https://youtu.be/Xfu-sk1qL0M?si=IryyFEq78KhpPZ7H')
    else:
        await bot.send_document(call.message.chat.id, document=pdf_file)
        await bot.send_message(call.message.chat.id,
                               'Привет уважаемый пользователь, подробнее о нашем марафоне вы можете узнать в презентации либо по ссылке https://www.youtube.com/watch?v=YMDgshmHc1o')


@dp.callback_query_handler(text_startswith='zadaniyetrainer2_')
async def load_name(call: CallbackQuery):
    number = call.data.split("_")[1]
    if number == "en":
        await bot.send_video(call.message.chat.id, video=video_vst, caption=text_vst)
    else:
        await bot.send_video(call.message.chat.id, video=video_vst, caption=text_vst_ru)


@dp.callback_query_handler(text_startswith='zadaniyetrainer_')
async def load_name(call: CallbackQuery):
    try:
        number = call.data.split("_")[1]
        language = cur.execute(f'SELECT language FROM akk WHERE id_akk={call.message.chat.id}').fetchone()[0]
        a = cur.execute(
            f'SELECT name_video, description from instruct WHERE id={number} and language="{language}"').fetchone()
        kr = ''
        if not (a[1] is None):
            kr = a[1]
        if a[0] == '-1000':
            await bot.send_message(call.message.chat.id, text=a[1])
        else:
            if a[0].split('<>')[0] == 'photo':
                try:
                    await bot.send_photo(call.message.chat.id, photo=a[0].split('<>')[1], caption=kr)
                except Exception as e:
                    print(e)
            else:
                if a[0].split('<>')[0] == 'file':
                    try:
                        await bot.send_document(call.message.chat.id, document=a[0].split('<>')[1], caption=kr)
                        # try:
                        #     await bot.send_message(call.message.chat.id, text=kr)
                        # except Exception as e:
                        #     print(e)
                    except Exception as e:
                        print(e)
                else:
                    try:
                        await bot.send_video(call.message.chat.id, video=a[0], caption=kr)
                    except Exception as e:
                        print(e)
    except Exception as e:
        await call.message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.callback_query_handler(text_startswith='zadantran_')
async def load_name(call: CallbackQuery):
    try:
        number = call.data.split("_")[1]
        language = cur.execute(f'SELECT language FROM akk WHERE id_akk={call.message.chat.id}').fetchone()[0]
        a = cur.execute(
            f'SELECT name_video, description from zagatovka WHERE id={number} and language="{language}"').fetchone()
        kr = ''
        if not (a[1] is None):
            kr = a[1]
        if a[0] == '-1000':
            await bot.send_message(call.message.chat.id, text=a[1])
        else:
            if a[0].split('<>')[0] == 'photo':
                try:
                    await bot.send_photo(call.message.chat.id, photo=a[0].split('<>')[1], caption=kr)
                except Exception as e:
                    print(e)
            else:
                if a[0].split('<>')[0] == 'file':
                    try:
                        await bot.send_document(call.message.chat.id, document=a[0].split('<>')[1], caption=kr)
                    except Exception as e:
                        print(e)
                else:
                    if a[0].split('<>')[0] == 'audio':
                        try:
                            await bot.send_audio(call.message.chat.id, audio=a[0].split('<>')[1], caption=kr)
                        except Exception as e:
                            print(e)
                    else:
                        try:
                            await bot.send_video(call.message.chat.id, video=a[0], caption=kr)
                        except Exception as e:
                            print(e)
    except Exception as e:
        await call.message.answer('Какая-то ошибка, попробуйте еще раз')


@dp.message_handler(text='Сменить язык')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        keyboard_inline = InlineKeyboardMarkup(row_width=1)
        Buter1 = InlineKeyboardButton(text="Русский", callback_data=f"podpiskut_ru")
        Buter2 = InlineKeyboardButton(text="English", callback_data=f"podpiskut_en")
        keyboard_inline.add(Buter1, Buter2)
        await message.answer('Выберите язык', reply_markup=keyboard_inline)


@dp.message_handler(text='Change the language')
async def load_name(message: types.Message):
    if message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        keyboard_inline = InlineKeyboardMarkup(row_width=1)
        Buter1 = InlineKeyboardButton(text="Русский", callback_data=f"podpiskut_ru")
        Buter2 = InlineKeyboardButton(text="English", callback_data=f"podpiskut_en")
        keyboard_inline.add(Buter1, Buter2)
        await message.answer('Select a language', reply_markup=keyboard_inline)


@dp.callback_query_handler(text_startswith='podpt_')
async def load_name(call: CallbackQuery):
    try:
        name = call.data.split("_")[1]
        # cur.execute(
        #     f'INSERT INTO akk (akk_id,language) VALUES ({int(call.message.chat.id)}, "{name}")')
        # base.commit()
        if name == "en":
            butt1 = InlineKeyboardButton(text="About the marathon", callback_data=f"zadaniyetrainer1_en")
            butt2 = InlineKeyboardButton(text="An example of rils", callback_data=f"zadaniyetrainer2_en")
            keyboard_inline1 = InlineKeyboardMarkup(row_width=1)
            keyboard_inline1.insert(butt1)
            keyboard_inline1.insert(butt2)
            butt3 = InlineKeyboardButton(text="Join the marathon", callback_data=f"podpiskier_en")
            keyboard_inline1.insert(butt3)
            text = 'Welcome to the marathon🥳'
        else:
            butt1 = InlineKeyboardButton(text="О марафоне", callback_data=f"zadaniyetrainer1_ru")
            butt2 = InlineKeyboardButton(text="Пример рилсов", callback_data=f"zadaniyetrainer2_ru")
            keyboard_inline1 = InlineKeyboardMarkup(row_width=1)
            keyboard_inline1.insert(butt1)
            keyboard_inline1.insert(butt2)
            butt3 = InlineKeyboardButton(text="Вступить в марафон", callback_data=f"podpiskier_ru")
            keyboard_inline1.insert(butt3)
            text = 'Добро пожаловать в марафон🥳'
        await call.message.answer(text, reply_markup=keyboard_inline1)
    except Exception as e:
        await bot.send_message(call.message.chat.id, 'какая-то ошибка')


@dp.callback_query_handler(text_startswith='podpiskut_')
async def load_name(call: CallbackQuery):
    if call.message.chat.id in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            name = call.data.split("_")[1]
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            if name == "ru":
                cur.execute(
                    f'UPDATE akk SET language="ru" WHERE id_akk={int(call.message.chat.id)}')
                base.commit()
                but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
                but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
                but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
                but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
                but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
                but6 = KeyboardButton(text="Чат")
                but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
                but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
                keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                await call.message.answer('Поздравляем, язык изменен', reply_markup=keyboard_inline)
            else:
                if name == "en":
                    cur.execute(
                        f'UPDATE akk SET language="en" WHERE id_akk={int(call.message.chat.id)}')
                    base.commit()
                    but1 = KeyboardButton(text="Complete the task", callback_data=f"zadaniye_vip")
                    but2 = KeyboardButton(text="View tasks", callback_data=f"zadaniye_look")
                    but3 = KeyboardButton(text="View the rating", callback_data=f"zadaniye_lookppp")
                    but4 = KeyboardButton(text="Lessons", callback_data=f"zadaniye_lesson")
                    but5 = KeyboardButton(text="Instruction", callback_data=f"zadaniye_lesson")
                    but6 = KeyboardButton(text="Chat")
                    but7 = KeyboardButton(text="Change the language", callback_data=f"zadaniye_lesson")
                    but8 = KeyboardButton(text="Blanks", callback_data=f"zadaniye_lesson")
                    keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                    await call.message.answer('Congratulations, the language has been changed',
                                              reply_markup=keyboard_inline)
        except Exception as e:
            await bot.send_message(call.message.chat.id, 'какая-то ошибка')


@dp.callback_query_handler(text='podpiski')
async def load_name(call: CallbackQuery):
    # butt5 = InlineKeyboardButton(text="О марафоне", callback_data=f"zadaniyetrainer1")
    # butt1 = InlineKeyboardButton(text="«Start»", callback_data=f"podpiskier_start")
    # butt2 = InlineKeyboardButton(text="«Guest»", callback_data=f"podpiskier_guest")
    # butt4 = InlineKeyboardButton(text="«Business»", callback_data=f"podpiskier_business")
    # keyboard_inline1 = InlineKeyboardMarkup(row_width=1)
    # keyboard_inline1.insert(butt1)
    # keyboard_inline1.insert(butt2)
    # keyboard_inline1.insert(butt4)
    # keyboard_inline1.insert(butt5)
    if call.message.chat.id not in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        keyboard_inline = InlineKeyboardMarkup(row_width=1)
        Buter1 = InlineKeyboardButton(text="Русский", callback_data=f"podpiskier_ru")
        Buter2 = InlineKeyboardButton(text="English", callback_data=f"podpiskier_en")
        keyboard_inline.add(Buter1, Buter2)
        await call.message.answer('Select a language', reply_markup=keyboard_inline)
    else:
        await call.message.answer('You are already in the marathon')


#     await call.message.answer('''Тарифы:
# «Start»:
# 1000₽ участие +
# общие обучения и видео уроки
#
# «Guest»
# 5000₽ +
# индивидуальная консультация и составленная
# программа на 60 дней с нутрицологом и тренером
#
# «Business»
# 60к-120к₽ бизнес
# покупка продукции +монетизация своего участия +
# индивидуальные программы от нутрицолога и тренера
#
# Также вы можете ознакомиться с марафоном
# нажав на кнопку О марафоне''', reply_markup=keyboard_inline1)


@dp.message_handler(text_startswith='add_time_')
async def register_friends_hourss(message: types.Message, state: FSMContext):
    if message.chat.id in admin_id:
        try:
            a = int(message.text.split("_")[2])
            schedulerer1 = AsyncIOScheduler(timezone='Europe/Moscow')
            schedulerer1.add_job(noon_print4, trigger='date', run_date=datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=a),
                                 kwargs={'bot': bot})
            schedulerer1.start()
            await message.answer(f'Все хорошо, время {a} часов, {datetime.now(pytz.timezone("Europe/Moscow"))}')
        except Exception as e:
            print(e)
            await message.answer('Что-то не так')


@dp.callback_query_handler(text_startswith='podpiskier_')
async def load_name(call: CallbackQuery):
    # it = ''
    # name = call.data.split("_")[1]
    # if name == 'free' or name == 'business':
    #     await bot.send_photo(call.message.chat.id, photo=item_url1b, caption='Свяжитесь со мной: https://t.me/maks_afanasiev')
    #     # await call.message.answer('Заполните форму и мы с вами свяжемся: https://t.me/maks_afanasiev')
    # else:
    #     if name == 'start':
    #         it = item_url
    #     else:
    #         it = item_url1
    #     try:
    #         a = itemer_podpiski[name]
    #         await bot.send_invoice(call.message.chat.id,
    #                                title=a['item_title'],
    #                                description=a['item_description'],
    #                                provider_token=PAYMENTS_TOKEN,
    #                                currency='rub',
    #                                photo_url=it,
    #                                photo_height=520,
    #                                photo_width=520,
    #                                # photo_size=240,
    #                                need_name=False,
    #                                need_email=False,
    #                                need_phone_number=False,
    #                                need_shipping_address=False,
    #                                # protect_content=True,
    #                                # is_flexible=False,
    #                                prices=[LabeledPrice(label=a['item_title'], amount=a['cost'])],
    #                                start_parameter='example',
    #                                payload='some_invoice')
    #     except Exception as e:
    #         print(e)
    if call.message.chat.id not in [row[0] for row in cur.execute(f'SELECT id_akk FROM akk').fetchall()]:
        try:
            name = call.data.split("_")[1]
            art = ''
            if call.message.chat.username == "None" or call.message.chat.username is None:
                art = str(call.message.chat.id)
            else:
                art = call.message.chat.username
            cur.execute(
                f'INSERT INTO akk(id_akk, raiting, username, language) VALUES ({call.message.chat.id}, 0, "@{art}", "{name}")')
            cur.execute(f'INSERT INTO parashut(id_akk, col) VALUES ({call.message.chat.id}, 3)')
            base.commit()
            keyboard_inline = ReplyKeyboardMarkup(resize_keyboard=True)
            if name == "ru":
                but1 = KeyboardButton(text="Выполнить задание", callback_data=f"zadaniye_vip")
                but2 = KeyboardButton(text="Посмотреть задания", callback_data=f"zadaniye_look")
                but3 = KeyboardButton(text="Посмотреть рейтинг", callback_data=f"zadaniye_lookppp")
                but4 = KeyboardButton(text="Уроки", callback_data=f"zadaniye_lesson")
                but5 = KeyboardButton(text="Инструкция", callback_data=f"zadaniye_lesson")
                but6 = KeyboardButton(text="Чат")
                but7 = KeyboardButton(text="Сменить язык", callback_data=f"zadaniye_lesson")
                but8 = KeyboardButton(text="Заготовки", callback_data=f"zadaniye_lesson")
                keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                await call.message.answer('Поздравляем, все задания будут представлены на выбранном языке',
                                          reply_markup=keyboard_inline)
                await bot.send_video(call.message.chat.id,
                                     caption='''Добро пожаловать на марафон, кликай по кнопкам и узнавай полезную информацию''',
                                     reply_markup=keyboard_inline, video=video_privet)
            else:
                if name == "en":
                    but1 = KeyboardButton(text="Complete the task", callback_data=f"zadaniye_vip")
                    but2 = KeyboardButton(text="View tasks", callback_data=f"zadaniye_look")
                    but3 = KeyboardButton(text="View the rating", callback_data=f"zadaniye_lookppp")
                    but4 = KeyboardButton(text="Lessons", callback_data=f"zadaniye_lesson")
                    but5 = KeyboardButton(text="Instruction", callback_data=f"zadaniye_lesson")
                    but6 = KeyboardButton(text="Chat")
                    but7 = KeyboardButton(text="Change the language", callback_data=f"zadaniye_lesson")
                    but8 = KeyboardButton(text="Blanks", callback_data=f"zadaniye_lesson")
                    keyboard_inline.add(but2, but1, but5, but3, but4, but8, but6, but7)
                    await call.message.answer('Congratulations, all tasks will be presented in the selected language',
                                              reply_markup=keyboard_inline)
                    await bot.send_video(call.message.chat.id,
                                         caption='''Welcome to the marathon, click on the buttons and find out useful information''',
                                         reply_markup=keyboard_inline, video=video_privet)
        except Exception as e:
            await bot.send_message(call.message.chat.id, 'какая-то ошибка')
        try:
            text = ''
            a = cur.execute(
                f'SELECT name_video,description  FROM zadaniya WHERE number=0 and language="{name}"').fetchone()
            if a[0] != '-1000':
                if a[0].split("^")[0] == 'photo':
                    await bot.send_photo(call.message.chat.id, photo=a[0].split("^")[1])
                else:
                    await bot.send_video(call.message.chat.id, video=a[0])
            if a[1] != '':
                text += a[1]
            await bot.send_message(call.message.chat.id, text=text)
        except Exception as e:
            await call.message.answer('Какая-то ошибка, попробуйте еще раз')


# @dp.pre_checkout_query_handler(lambda q: True)
# async def checkout_process(pre_checkout_query: PreCheckoutQuery):
#     await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
#
#
# @dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
# async def successful_payment(message: Message):
#     try:
#         cur.execute(
#             f'INSERT INTO akk(id_akk, raiting, username) VALUES ({message.chat.id}, 0, "@{message.from_user.username}")')
#         cur.execute(f'INSERT INTO parashut(id_akk, col) VALUES ({message.chat.id}, 3)')
#         base.commit()
#     except Exception as e:
#         await bot.send_message(message.chat.id, 'какая-то ошибка')
#     pmnt = message.successful_payment.to_python()
#     print(pmnt['total_amount'])
#     flag = 0
#     flashok = 0
#     if 100000 == pmnt['total_amount']:
#         a = itemer_podpiski['start']
#         flag = 1
#         await bot.send_message(admin_id[0],
#                                f'ID:{message.chat.id}\nUsername: {message.from_user.username}\n Оплатила подписку: Start')
#         await bot.send_message(admin_id[1],
#                                f'ID:{message.chat.id}\nUsername: {message.from_user.username}\n Оплатила подписку: Start')
#     else:
#         if 500000 == pmnt['total_amount']:
#             a = itemer_podpiski['guest']
#             flag = 1
#             flashok = 1
#             await bot.send_message(admin_id[0],
#                                    f'ID:{message.chat.id}\nUsername: {message.from_user.username}\n Оплатила подписку: Guest')
#             await bot.send_message(admin_id[1],
#                                    f'ID:{message.chat.id}\nUsername: {message.from_user.username}\n Оплатила подписку: Guest')
#         else:
#             if 10000 == pmnt['total_amount']:
#                 a = itemer_podpiski['guest']
#                 flag = 1
#                 await bot.send_message(admin_id[0],
#                                        f'ID:{message.chat.id}\nUsername: {message.from_user.username}\n Оплатила подписку: Start')
#                 await bot.send_message(admin_id[1],
#                                        f'ID:{message.chat.id}\nUsername: {message.from_user.username}\n Оплатила подписку: Start')
#     if flag:
#         await bot.send_message(
#             message.chat.id,
#             a['successful_payment'].format(total_amount=message.successful_payment.total_amount // 100,
#                                            currency=message.successful_payment.currency)
#         )
#     if flashok:
#         await bot.send_message(message.chat.id, 'https://t.me/vip_wave - чат для персонального общения и консультаций личных')


if __name__ == '__main__':
    print("Server start successful!")
    sql_start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
