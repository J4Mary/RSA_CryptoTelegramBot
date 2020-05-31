import telebot
import rsa
import config

bot = telebot.TeleBot(config.TOKEN)
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('Получить открытый и закрытый ключ', 'Зашифровать сообщение', 'Расшифровать соообщение')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Привет, выбери, что тебе нужно '
                     '(если ты в первый раз здесь, сформируй свои ключи и сохрани их)',
                     reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'получить открытый и закрытый ключ':
        (pubkey, privkey) = rsa.newkeys(1024)
        public_file = open('public.pem', mode='wb')
        public_file.write(pubkey.save_pkcs1('PEM'))
        privat_file = open('private.pem', mode='wb')
        privat_file.write(privkey.save_pkcs1('PEM'))
        bot.send_message(message.chat.id, 'Твой открытый ключ:')
        public_file = open('public.pem', 'rb')
        bot.send_document(message.chat.id, public_file)

        bot.send_message(message.chat.id, 'Твой закрытый ключ:')
        privat_file = open('private.pem', 'rb')
        bot.send_document(message.chat.id, privat_file)

    elif message.text.lower() == 'зашифровать сообщение':
        msg = bot.send_message(message.chat.id, 'Пришли мне открытый ключ того, кому ты хочешь отправить сообщение')
        bot.register_next_step_handler(msg, Encryption.ask_key)
        #encrypt(get_public_key, get_text)
    elif message.text.lower() == 'расшифровать соообщение':
        bot.send_sticker(message.chat.id, 'CAADAgADZgkAAnlc4gmfCor5YbYYRAI')


class Encryption:
    @staticmethod
    @bot.message_handler(content_types=['file'])
    def ask_key(message):
        file = bot.getFile(message.file[-1].file_id)
        file.download('user_public.pem')
        msg = bot.send_message(message.chat.id, 'Пришли мне текст, который ты хочешь зашифровать')
        bot.register_next_step_handler(msg, Encryption.ask_message)

    @staticmethod
    @bot.message_handler(content_types=['text'])
    def ask_message(message):
        with open('user_public.pem', mode='rb') as public_file:
            keydata = public_file.read()
            public_key = rsa.PublicKey.load_pkcs1(keydata, 'PEM')
        en_message = rsa.encrypt(message.text.encode('utf8'), public_key)
        bot.send_message(message.chat.id, 'Зашифрованное сообщение:')
        bot.send_message(message.chat.id, en_message)





bot.polling(none_stop=True)