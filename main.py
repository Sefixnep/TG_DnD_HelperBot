from Auxiliary.chat import *


@bot.message_handler(commands=["start"])
def start(message_tg):
    message_start.new_line(message_tg)


@bot.callback_query_handler(func=lambda call: True)
def callback_reception(call):
    for button in buttons_lst:  # Найти кнопку в виде объекта класса Button
        if button.callback_data == call.data and button.for_messages:
            message_for = button(call.message)
            if message_for(call.message) is None:
                message_for.old_line(call.message)  # Выводить сообщение к которому ведет кнопка

    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)


@bot.message_handler(content_types=['text'])
def watch(message_tg):
    Message.userSendLogger(message_tg)


if __name__ == '__main__':
    logger.info(f'{config.Bot} start')

bot.infinity_polling()
