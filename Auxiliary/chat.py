import telebot
from loguru import logger
from telebot.types import InputMediaPhoto

from Auxiliary import chatgpt, config

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='html')

start_prompt = ('Ты профессиональный помощник мастера игры "Подземелья и драконы". '
                'ты должен разбираться в правилах игры и точно следовать предпочтениям и указаниям пользователя. '
                'При выдачи ответа пользователю, каждый заголовок обособляй символом *')

dict_default_prompts = {
    'location': 'тебе необходимо придумать локации (мобы которых можно встретить) и '
                'подробно их расписать обязательно четко по шаблону:\n'
                '*Локация*: ...\n\n'
                '*Вид*: ...\n\n'
                '*Описание*: ...\n\n'
                '*Основные элементы*:\n\n'
                '- ...\n'
                '- ...',
    'quest': 'тебе необходимо придумать квесты, нужно придумывать их для '
             'созданных ранее тобой локаций, если они были, Для квеста распиши подробно:\n'
             '-Описание квеста и места его выполнения\n'
             '-Заказчика квеста\n'
             '-Трудности и враги на пути\n'
             '-Награда за квест\n',
    'character': 'тебе необходимо придумать персонажей, следуй основным критериям и '
                 'правилам создания из правил игры, делай обязательно четко по шаблону:\n'
                 '*Персонаж*: ...\n\n'
                 '*Вид*: ...\n\n'
                 '*Предистория*: ...\n\n'
                 '*Характер и мотивация*: ...\n\n'
                 '*Навыки и экипировка*: ...',
    'plottwist': 'тебе необходимо придумать сюжетные повороты, нужно использовать '
                 'созданных тобой персонажей и квесты, если они есть, распиши подробно:\n'
                 '-Описание действий\n'
                 '-Участников события\n'
                 '-Последствия события',
    'evil': 'тебе необходимо придумать несколько сценариев битв со злодеями, злодеев тоже придумай и '
            'опиши, можешь использовать созданных тобой персонажей и квесты если они есть, распиши подробно:\n'
            '-Описание и предысторию злодея\n'
            '-Сценарий битвы с ним\n'
            '-Возможные финалы битвы\n'
            '-Последствия битвы',
    'final': 'тебе необходимо придумать несколько вариантов завершения истории, можешь использовать '
             'ранее придуманные квесты, персонажей и другое, если они есть, подробно распиши:\n'
             '-Предысторию завершения\n'
             '-Участников завершения\n'
             '-Что будет потом\n',
}

dict_chats = dict()
buttons_lst = list()


class Message:
    def __init__(self, text, buttons=None, *buttons_for, func=lambda *args: None):
        self.__text = text
        self.__buttons = buttons  # Двумерный кортеж с кнопками в виде InlineKeyboardButton
        self.__board_tg = None
        if buttons:
            self.__board_tg = telebot.types.InlineKeyboardMarkup()
            for row in (map(lambda x: x.button_tg, buttons1D) for buttons1D in buttons):
                self.__board_tg.row(*row)
        for button_for in buttons_for:
            button_for.for_messages += (self,)
        self.__func = func

    def __call__(self, *args):
        return self.__func(*args)

    def __getitem__(self, item):
        return self.__buttons[item[0]][item[1]]

    def new_line(self, message_tg, delete_message=True, userSendLogger=True):
        if userSendLogger:
            self.userSendLogger(message_tg)
        if delete_message:
            bot.delete_message(message_tg.chat.id, message_tg.id)
        return self.__botSendMessage(message_tg)

    def old_line(self, message_tg, text=None, userSendLogger=False):
        if userSendLogger:
            self.userSendLogger(message_tg, text)
        return self.__botEditMessage(message_tg)

    @staticmethod
    def __trueText(text, message_tg):
        if "%" in text:
            return text % (str(message_tg.chat.id),) * text.count("%")
        return text

    @staticmethod
    def userSendLogger(message_tg, text=None):
        if text is None:
            if '\n' in message_tg.text:
                logger.info(f'{message_tg.from_user.username} ({message_tg.chat.id}): \n{message_tg.text}')
            else:
                logger.info(f'{message_tg.from_user.username} ({message_tg.chat.id}): {message_tg.text}')
        else:
            if '\n' in text:
                logger.info(f'{message_tg.chat.username} ({message_tg.chat.id}): \n{text}')
            else:
                logger.info(f'{message_tg.chat.username} ({message_tg.chat.id}): {text}')

    def __botSendMessage(self, message_tg, parse_mode='MARKDOWN', indent=3):
        text = self.__trueText(self.__text, message_tg)
        botMessage = bot.send_message(chat_id=message_tg.chat.id, text=text, reply_markup=self.__board_tg,
                                      parse_mode=parse_mode)
        if self.__board_tg is None:
            if '\n' in text:
                logger.info(f"{config.Bot} ({botMessage.chat.username}, {message_tg.chat.id}):\n{text}\n")
            else:
                logger.info(f"{config.Bot} ({botMessage.chat.username}, {message_tg.chat.id}): {text}")
        else:
            reply_markup_text = ''
            for reply_markup1 in botMessage.json['reply_markup']['inline_keyboard']:

                for reply_markup2 in reply_markup1:
                    reply_markup_text += f'[{reply_markup2["text"]}]' + (' ' * indent)
                reply_markup_text = reply_markup_text[:-indent]

                reply_markup_text += '\n'
            reply_markup_text = reply_markup_text[:-1]
            logger.info(
                f"{config.Bot} ({botMessage.chat.username}, {message_tg.chat.id}):\n{text}\n{reply_markup_text}\n")
        return botMessage

    def __botEditMessage(self, message_tg, parse_mode='MARKDOWN', indent=3):
        text = self.__trueText(self.__text, message_tg)
        botMessage = bot.edit_message_text(chat_id=message_tg.chat.id, message_id=message_tg.id, text=text,
                                           reply_markup=self.__board_tg,
                                           parse_mode=parse_mode)
        if self.__board_tg is None:
            if '\n' in text:
                logger.info(f"{config.Bot} ({botMessage.chat.username}, {message_tg.chat.id}):\n{text}\n")
            else:
                logger.info(f"{config.Bot} ({botMessage.chat.username}, {message_tg.chat.id}): {text}")
        else:
            reply_markup_text = ''
            for reply_markup1 in botMessage.json['reply_markup']['inline_keyboard']:

                for reply_markup2 in reply_markup1:
                    reply_markup_text += f'[{reply_markup2["text"]}]' + (' ' * indent)
                reply_markup_text = reply_markup_text[:-indent]

                reply_markup_text += '\n'
            reply_markup_text = reply_markup_text[:-1]
            logger.info(
                f"{config.Bot} ({botMessage.chat.username}, {message_tg.chat.id}):\n{text}\n{reply_markup_text}\n")
        return botMessage


class Button:
    def __init__(self, text, callback_data, *for_messages, func=lambda *args: None):
        self.text = text
        self.callback_data = callback_data
        self.button_tg = telebot.types.InlineKeyboardButton(self.text, callback_data=self.callback_data)
        self.for_messages = for_messages
        self.__func = func
        buttons_lst.append(self)

    def __call__(self, message_tg, userSendLogger=True):
        if userSendLogger:
            Message.userSendLogger(message_tg, f'[{self.text}]')
        if self.__func(self.for_messages, message_tg) is None:
            return self.for_messages[0]
        return self.__func(self.for_messages, message_tg)


def clear_next_step_handler(_, message_tg):
    bot.clear_step_handler_by_chat_id(message_tg.chat.id)


def receiver(botMessage, task, photos=None):
    def wrapper(message_tg):
        nonlocal botMessage
        Message.userSendLogger(message_tg)
        bot.delete_message(message_tg.chat.id, message_tg.id)
        try:
            botMessage = message_processing.old_line(botMessage)

            chat = dict_chats[message_tg.chat.id]
            text = dict_default_prompts[task]

            chat.message(text, system=True, answer=False)
            ans = chat.message(message_tg.text)

            if photos is not None:
                descriptions = list(filter(lambda string: photos.lower() in string.lower(), ans.split("\n\n")))

                # Создаем список медиа объектов
                media_group = [InputMediaPhoto(chat.create_image(f"Красивое {task} для игры в DND" + descriptions[i]
                                                                 .replace("#", "")))
                               for i in range(len(descriptions))]

                bot.send_media_group(message_tg.chat.id, media_group)

            Message(ans).new_line(botMessage, botMessage.text)
        except Exception as exc:
            print(f"Exception: {exc}")
            message_start.old_line(botMessage)
        else:
            message_menu.new_line(message_tg, delete_message=False)

    return wrapper


def location(message_tg):
    botMessage = message_location.old_line(message_tg, message_tg.text)
    bot.clear_step_handler_by_chat_id(message_tg.chat.id)
    bot.register_next_step_handler(botMessage, receiver(botMessage, "location", "Вид"))
    return True


def quest(message_tg):
    botMessage = message_quest.old_line(message_tg, message_tg.text)
    bot.clear_step_handler_by_chat_id(message_tg.chat.id)
    bot.register_next_step_handler(botMessage, receiver(botMessage, "quest"))
    return True


def character(message_tg):
    botMessage = message_character.old_line(message_tg, message_tg.text)
    bot.clear_step_handler_by_chat_id(message_tg.chat.id)
    bot.register_next_step_handler(botMessage, receiver(botMessage, "character", "Вид"))
    return True


def plottwist(message_tg):
    botMessage = message_plottwist.old_line(message_tg, message_tg.text)
    bot.clear_step_handler_by_chat_id(message_tg.chat.id)
    bot.register_next_step_handler(botMessage, receiver(botMessage, "plottwist"))
    return True


def evil(message_tg):
    botMessage = message_evil.old_line(message_tg, message_tg.text)
    bot.clear_step_handler_by_chat_id(message_tg.chat.id)
    bot.register_next_step_handler(botMessage, receiver(botMessage, "evil"))
    return True


def final(message_tg):
    botMessage = message_final.old_line(message_tg, message_tg.text)
    bot.clear_step_handler_by_chat_id(message_tg.chat.id)
    bot.register_next_step_handler(botMessage, receiver(botMessage, "final"))
    return True


def new_chat(_, message_tg):
    chat = chatgpt.Chat()
    chat.message(start_prompt, system=True, answer=False)
    dict_chats[message_tg.chat.id] = chat


def delete_chat(_, message_tg):
    if message_tg.chat.id in dict_chats:
        dict_chats.pop(message_tg.chat.id)


message_start = Message(f"Ваш ID: `%s`\n"
                        f"😺Привет, я персональный помощник для мастеров игры 'Подземелья и драконы'😺\n"
                        f"Нажимай на кнопку 'Начать игру' и давай создадим интересную и увлекательную историю\n"
                        f"*По всем вопросам:*\n"
                        f"├ `Родионов Семён` (@Sefixnep)\n"
                        f"└ `Вершинин Михаил` (@Radsdafar08)",
                        ((Button("Начать игру", "start_game", func=new_chat),),))

message_menu = Message(f'Выберите неоходимую вам функцию (советуем выбирать по порядку)',
                       (
                           (Button('Придумать локацию', 'location'),
                            Button('Придумать квест', 'quest')), (
                               Button('Придумать персонажа', 'character'),
                               Button('Придумать сюжетный поворот', 'plottwist')), (
                               Button('Придумать бой с злодеем', 'evil'),
                               Button('Придумать завершение истории', 'final')),
                           (Button('Получить фоновую музыку для игры', 'music'),),
                           (Button('🔙 Завершить игру 🔙', 'back', message_start, func=delete_chat),)),
                       message_start[0, 0])

message_location = Message(f'Расскажи, сколько локаций тебе нужно, и если у тебя есть предпочтения, то напиши их',
                           (
                               (Button('🔙 Вернуться в меню 🔙', 'back_menu', message_menu,
                                       func=clear_next_step_handler),),),
                           message_menu[0, 0],
                           func=location)

message_quest = Message(
    f'Скажи, сколько квестов тебе необходимо, и если у тебя есть предпочтения, то напиши о них подробно',
    ((message_location[0, 0],),), message_menu[0, 1], func=quest)

message_character = Message(
    f'Скажи, сколько персонажей тебе необходимо, и если у тебя есть предпочтения, то напиши о них подробно',
    ((message_location[0, 0],),), message_menu[1, 0], func=character)

message_plottwist = Message(
    f'Скажи, сколько сюжетных поворотов тебе необходимо, и если у тебя есть предпочтения, то напиши о них подробно',
    ((message_location[0, 0],),), message_menu[1, 1], func=plottwist)

message_evil = Message(
    f'Скажи, сколько боёв со злодеями тебе необходимо, и если у тебя есть предпочтения, то напиши о них подробно',
    ((message_location[0, 0],),), message_menu[2, 0], func=evil)

message_final = Message(
    f'Скажи, сколько вариантов завершения истории тебе необходимо, и если у тебя есть предпочтения, то напиши о них '
    f'подробно',
    ((message_location[0, 0],),), message_menu[2, 1], func=final)

message_music = Message(
    f'Ссылка на фоновые композиции:\n'
    f'https://www.youtube.com/watch?v=vIFwdiUtl4M&list=PLc6qbgdpAzTzw3VZ6QiMBjZ9r8QUzh-lc',
    ((message_location[0, 0],),), message_menu[3, 0]
)

message_processing = Message("*Ваш запрос обрабатывается!* _(время ожидания 10-300 сек)_")
