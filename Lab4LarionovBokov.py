from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
import os

bot_token=os.getenv('TELEGRAM_BOT_TOKEN') #передаем токен бота в переменную
bot = Bot(token=bot_token) #вызов бота по токену
dp=Dispatcher(bot, storage=MemoryStorage())#запуск бота с праметром, что использованием хранилища данных

class Form(StatesGroup): #создание группы статусов
    name = State()
    rate = State()
    convert = State()
    num = State()

currencies = {} #создание коллекции для записи разных валют


@dp.message_handler(commands=['start']) #обработчик запускающий процесс при получении команды /start
async def start(message: types.Message): #вызов функции асинхронным (не по порядку, а по событию) методом
    await message.reply("Привет! Я бот для подсчёта валюты.") #отправка текстового сообщения в бота

#При написании команды /save_currency срвбатывает следующая функция
@dp.message_handler(commands=['save_currency'])#обработчик запускающий процесс при получении команды /save_currency
async def save(message: types.Message):
    await Form.name.set()#устанавливает статус name для активации события
    await message.reply("Введите название валюты")#отправка текстового сообщения в бота

@dp.message_handler(state=Form.name)#вызов функции при установке статуса name (await Form.name.set)
async def name(message: types.Message, state: FSMContext):#вызов функции асинхронным (не по порядку, а по событию) методом
    await state.update_data(name=message.text)#сохранение текста полученного из бота в созданную переменную name
    await Form.rate.set()#устанавливает статус rate для активации события
    await message.reply('В 1 "' + message.text + '" рублей= ')#отправка текстового сообщения в бота

@dp.message_handler(state=Form.rate)#вызов функции при установке статуса rate (await Form.rate.set)
async def rate(message: types.Message, state: FSMContext):
    rate=message.text#в переменную записываем сообщение из бота
    name = await state.get_data()#создание ключа(контрольного слова)
    name_currency= name['name']#запись ключа(контрольного слова)
    currencies[name_currency] = rate#запись сохранение данных по ключу(контрольного слова)
    await message.reply("Сохранено")  # отправка текстового сообщения в бота
    await state.finish()


@dp.message_handler(commands=['convert'])#обработчик запускающий процесс при получении команды /convert
async def convert(message: types.Message):
    await Form.convert.set()#устанавливает статус convert для активации события
    await message.reply("Введите название валюты")

@dp.message_handler(state=Form.convert)#вызов функции при установке статуса check (await Form.convert.set)
async def convert(message: types.Message, state: FSMContext):
    await state.update_data(cheack_rate=message.text)#сохранение текста полученного из бота в созданную переменную cheack_rate
    await Form.num.set()#устанавливает статус num для активации события
    await message.answer("Введите сумму для перевода в рубли")



@dp.message_handler(state=Form.num)#вызов функции при установке статуса num (await Form.num.set)
async def process_convert(message: types.Message, state: FSMContext):
    num = message.text #в переменную записываем сообщение из бота
    cheack_rate = await state.get_data() #создание ключа(контрольного слова)
    name_currency = cheack_rate['cheack_rate']#запись ключа(контрольного слова)
    result =int(num)* int(currencies[name_currency]) #запись сохранение данных по ключу(контрольного слова)
    await message.reply(result)#вывод результата
    await state.finish()#сброс статуса для выхода из функции

#точка входа в приложение, она позволяет работать боту в асинхронном режиме
if __name__ =='__main__':
    executor.start_polling(dp, skip_updates=True)