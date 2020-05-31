# coding=utf-8

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
        bot.register_next_step_handler(msg, Encryption.ask_pubkey)

    elif message.text.lower() == 'расшифровать соообщение':
        msg = bot.send_message(message.chat.id, 'Пришли мне свой закрытый ключ')
        bot.register_next_step_handler(msg, Decryption.ask_privkey)


class Encryption:
    @staticmethod
    @bot.message_handler(content_types=['document'])
    def ask_pubkey(message):
        try:
            # Скачивание файла в папку
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src = file_info.file_path
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, "Успешно сохранено")
        except Exception as e:
            bot.reply_to(message, e)
        msg = bot.send_message(message.chat.id, 'Пришли мне текст, который ты хочешь зашифровать')
        bot.register_next_step_handler(msg, Encryption.ask_message, file_info)

    @staticmethod
    @bot.message_handler(content_types=['text'])
    def ask_message(message, file_info):
        with open(file_info.file_path, mode='rb') as public_file:
            keydata = public_file.read()
            public_key = rsa.PublicKey.load_pkcs1(keydata, 'PEM')
        en_message = rsa.encrypt(message.text.encode('utf8'), public_key)
        encryption = open('crypto.txt', mode='wb')
        encryption.write(en_message)
        encryption = open('crypto.txt', 'rb')
        bot.send_message(message.chat.id, 'Зашифрованное сообщение:')
        bot.send_document(message.chat.id, encryption)


class Decryption:
    @staticmethod
    @bot.message_handler(content_types=['document'])
    def ask_privkey(message):
        try:
            # Скачивание файла в папку
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src = file_info.file_path
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, "Успешно сохранено")
        except Exception as e:
            bot.reply_to(message, e)
        msg = bot.send_message(message.chat.id, 'Пришли мне криптограмму')
        bot.register_next_step_handler(msg, Decryption.ask_crypto, file_info)

    @staticmethod
    @bot.message_handler(content_types=['document'])
    def ask_crypto(message, file_info):
        try:
            # Скачивание файла в папку
            file_crypto = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_crypto.file_path)

            cr = file_crypto.file_path
            with open(cr, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, "Успешно сохранено")
        except Exception as e:
            bot.reply_to(message, e)

        with open(file_info.file_path, mode='rb') as private_file:
            keydata = private_file.read()
            private_key = rsa.PrivateKey.load_pkcs1(keydata, 'PEM')

        with open(file_crypto.file_path, mode='rb') as crypto_file:
            crypto = crypto_file.read()
        decryption = rsa.decrypt(crypto, private_key)

        bot.send_message(message.chat.id, 'Расшифрованное сообщение:')
        bot.send_message(message.chat.id, decryption.decode('utf8'))


bot.polling(none_stop=True)
