import logging
import aiohttp
from datbase import Session
from datbase import Element
from telegram.ext import Application
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from T_IASS import BOT_TOKEN

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/help', '/map'],
                  ['/info', '/applicationto']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

"""START:"""


# start:
async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        "Привет!👋🏽\n"
        "🌿 Я telegram-бот от High Life, который поможет тебе...\n"
        "🚀 Легко и быстро подать заявку в Межднародную Аэрокосмическую Школу или узнать информацию о ней.\n"
        "📑 С чего начнём?) Чтобы подать заявку, используй команду /applicationto.\n"
        "ℹ Чтобы узнать о МАКШ, используй команду /info.\n"
        "📍 Чтобы посмотреть МАКШ на карте, используй команду /map.\n"
        "❗️Подать заявку можно только 1 раз!\n"
        "🚫 Изменить данные нельзя\n"
        "☁ Перед заявкой приготовьте ссылку на диск с вашими достижениями за последние 3 года и вашей фотографией",
        reply_markup=markup
    )


# help:
async def helper(update, context):
    await update.message.reply_text(
        "🚀 Чтобы подать заявку, используй команду /applicationto.\n"
        "ℹ Чтобы узнать о МАКШ, используй команду /info.\n"
        "📍 Чтобы посмотреть МАКШ на карте, используй команду /map.\n"
        "❗️Подать заявку можно только 1 раз!\n"
        "🚫 Изменить данные нельзя\n"
        "☁ Перед заявкой приготовьте ссылку на диск с вашими достижениями за последние 3 года и вашей фотографией"
    )


# info:
async def info(update, context):
    await context.bot.send_photo(
        update.message.chat_id,
        # Ссылка на картинку.
        "https://m.vk.com/photo-185042892_457240055",
        caption="🚀 МАКШ - это молодёжный летний лагерь-школа для школьников и студентов международного уровня.\n"
                "🔥 МАКШ создана по инициативе депутата Вячеслава Васильевича Аброщенко в 2010 году.\n"
                "📍 Находится лагерь в д. Калиновка Давлекановского района РБ.❤Там дети принимают участи в различных \n"
                "мероприятиях, конкурсах, слушают лекции космонавтов, инженеров и учёных, исторических личностей,\n"
                "героев СССР и РФ, потребляют здоровую пищу и занимаются спортом.\n"
                "😎 Туда попадают только лучшие дети со всей России, и даже со всего мира. 💸 Участие - бесплатное!",
    )


"""GEO:"""


# ll&spn:
def get_ll_spn(toponym):
    ll = list(map(lambda x: str(x), toponym["Point"]["pos"].split()))
    lowercorner = list(map(lambda x: float(x), toponym["boundedBy"]["Envelope"]["lowerCorner"].split()))
    uppercorner = list(map(lambda x: float(x), toponym["boundedBy"]["Envelope"]["upperCorner"].split()))
    spn = list(map(lambda x: str(x), [uppercorner[0] - lowercorner[0], uppercorner[1] - lowercorner[1]]))
    return ll, spn


# response:
async def get_response(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


# result:
async def geocoder(update, context):
    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"
    response = await get_response(geocoder_uri, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": "Республика Башкортостан, Давлекановский район, деревня Калиновка"
    }
                                  )

    toponym = response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    ll, spn = get_ll_spn(toponym)
    ll = ','.join(ll)
    spn = ','.join(spn)

    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
    await context.bot.send_photo(
        update.message.chat_id,
        # Ссылка на static API.
        static_api_request,
        caption="Мы здесь ❤:"
    )


"""APPLICATION"""

# создаём список для базы данных:
elements = []


# application:
async def applicationto(update, context):
    await update.message.reply_text(
        "🚀 Подаём заявку в МАКШ!)\n"
        "🛑 ты можешь прервать заявку, послав команду /stop.\n"
        "❗ Заявку можно подать только 1 раз, изменить данные нельзя. Не подавайте её 2 или более раза!\n"
        "📝 Напиши ФИО",
        reply_markup=ReplyKeyboardRemove()
    )

    return 1


# name:
async def l_f_p(update, context):
    name = update.message.text
    logger.info(name)
    global elements
    elements = [name]
    await update.message.reply_text(
        f"ФИО: {name}\n"
        "👦🏽 Сколько тебе лет?"
    )

    return 2


# age:
async def age(update, context):
    ager = update.message.text
    logger.info(ager)
    global elements
    elements.append(ager)
    await update.message.reply_text(
        f"Твой возраст: {ager}\n"
        "📞 Введи номер телефона"
    )

    return 3


# phone:
async def phone(update, context):
    phon = update.message.text
    logger.info(phon)
    global elements
    elements.append(phon)
    await update.message.reply_text(
        f"Твой телефон: {phon}\n"
        "💌 Введи свою почту"
    )

    return 4


# e-mail:
async def e_mail(update, context):
    mail = update.message.text
    logger.info(mail)
    global elements
    elements.append(mail)
    await update.message.reply_text(
        f"Твоя почта: {mail}\n"
        "❤ Как зовут родителя? (ФИО)"
    )

    return 5


# ФИО родителя:
async def parents_l_f_p(update, context):
    plfp = update.message.text
    logger.info(plfp)
    global elements
    elements.append(plfp)
    await update.message.reply_text(
        f"Родитель: {plfp}\n"
        "☎ Какой у него номер?"
    )

    return 6


# телефон родителя:
async def parents_phone(update, context):
    pphone = update.message.text
    logger.info(pphone)
    global elements
    elements.append(pphone)
    await update.message.reply_text(
        f"Телефон родителя: {pphone}\n"
        "📧 А почта?"
    )

    return 7


# почта родтеля:
async def parents_mail(update, context):
    pmail = update.message.text
    logger.info(pmail)
    global elements
    elements.append(pmail)
    await update.message.reply_text(
        f"Почта родителя: {pmail}\n"
        "☁ Теперь скинь ссылку на диск со своими достижениями и фотографией"
    )

    return 8


# ссылка на диск с достижениями и :
async def linker(update, context):
    link = update.message.text
    logger.info(link)
    global elements
    elements.append(link)
    await update.message.reply_text(
        f"Ссылка на достижения и фото: {link}\n"
        "🚀 Твоя заявка успешно отправлена, жди ответа (тебе позванят или напишут организаторы)! 💗",
        reply_markup=markup
    )

    session = Session()
    elements = [i.strip() for i in elements]
    element_name = elements[0]
    element_age = elements[1]
    element_phone = elements[2]
    element_e_mail = elements[3]
    element_parent = elements[4]
    element_parent_phone = elements[5]
    element_parent_e_mail = elements[6]
    element_achivements = elements[7]
    res = Element(name=element_name, age=element_age, phone=element_phone, e_mail=element_e_mail, parent=element_parent,
                  parent_phone=element_parent_phone, parent_e_mail=element_parent_e_mail,
                  achivements=element_achivements)
    session.add(res)
    '''element1 = Element(
        name=element_name.strip(),
        age=element_age.strip(),
        phone=element_phone.strip(),
        e_mail=element_e_mail.strip(),
        parent=element_parent.strip(),
        parent_phone=element_parent_phone.strip(),
        parent_e_mail=element_parent_e_mail.strip(),
        achivements=element_achivements.strip()
    )
    session.add(element1)'''

    session.commit()
    session.close()
    elements.clear()

    return ConversationHandler.END


# stop:
async def stop(update, context):
    global elements
    elements.clear()
    await update.message.reply_text(
        "Сделаем позже)",
        reply_markup=markup
    )

    return ConversationHandler.END


# handler:
conv_handler = ConversationHandler(
    # Точка входа в диалог.
    entry_points=[
        CommandHandler(
            'applicationto',
            applicationto
        )
    ],

    states={
        1: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            l_f_p
        )
        ],
        2: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            age
        )
        ],
        3: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            phone
        )
        ],
        4: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            e_mail
        )
        ],
        5: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            parents_l_f_p
        )
        ],
        6: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            parents_phone
        )
        ],
        7: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            parents_mail
        )
        ],
        8: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            linker
        )
        ],
    },

    # Точка прерывания диалога.
    fallbacks=[
        CommandHandler(
            'stop',
            stop
        )
    ]
)

"""ADDITIONALLY"""


# pics:
async def pics(update, context):
    await context.bot.sendMediaGroup(
        update.message.chat_id,
        [
            "https://m.vk.com/photo-185042892_457240065?list=photos-185042892",
            "https://m.vk.com/photo-185042892_457240063?list=photos-185042892",
            "https://m.vk.com/photo-185042892_457240060?list=photos-185042892",
            "https://m.vk.com/photo-185042892_457239996?list=photos-185042892"
        ]
    )


# main block:
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", helper))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("map", geocoder))
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
