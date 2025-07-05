import json
from telebot.async_telebot import AsyncTeleBot, types
import aiohttp
import datetime
import asyncio
import base64
import requests
import random
from datetime import datetime, timedelta
import time
import pyrule34
import sqlite3
import pyjokes
from bs4 import BeautifulSoup

url_rust = "https://play.rust-lang.org/execute"

MODEL_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

HEADERS = {"Authorization": "Bearer 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"}

ADMIN_LEVELS = {
	1:"Хелпер",
	2:"Модератор",
	3:"Админ"
}

conn = sqlite3.connect("collabs.db")
balances = sqlite3.connect("coins.db")
admins = sqlite3.connect("admins.db")
stories = sqlite3.connect("stories.db")
cursor = conn.cursor()
balcur = balances.cursor()
admcur = admins.cursor()
stcur = stories.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS collabs(chatid INTEGER PRIMARY KEY, name TEXT NOT NULL, song NOT NULL, players TEXT)")
conn.commit()
balcur.execute("CREATE TABLE IF NOT EXISTS coins(userid INTEGER PRIMARY KEY, coins INTEGER NOT NULL, abletowork INTEGER DEFAULT 1)")
balances.commit()
admcur.execute("CREATE TABLE IF NOT EXISTS admins(chatid INTEGER NOT NULL, userid INTEGER PRIMARY KEY, level INT NOT NULL)")
admins.commit()
stcur.execute("CREATE TABLE IF NOT EXISTS stories(chatid INTEGER PRIMARY KEY, content TEXT, active BOOLEAN DEFAULT 1)")
stories.commit()

with open("token.json") as f:
	json_token = json.load(f)['token']

bot = AsyncTeleBot(json_token)

async def irishuina(id):
		await bot.send_message(id, "ирис хуйня ебаная")
		
@bot.message_handler(commands=["createcollab"])
async def collab(message):
	try:
		print(message.text.split())
		name = message.text.split()[1]
		song = ' '.join(message.text.split()[2:])
		print(song)
		cursor.execute("INSERT INTO collabs (chatid, name, song) VALUES (?,?,?)", (message.chat.id, name, song))
		conn.commit()
		await bot.send_message(message.chat.id, "Коллаб создан!")
	except Exception as e:
		print(e)
		await bot.send_message(message.chat.id, "В этом чате уже есть коллаб/неправильно введена команда \nИспользование команды: \n/collab <имя> <название песни>")
		
@bot.message_handler(commands=["getcollab"])
async def getcollab(message):
	try:
		cursor.execute("SELECT name FROM collabs WHERE chatid=?",(message.chat.id,))
		name = cursor.fetchone()
		name = name[0]
		cursor.execute("SELECT song FROM collabs WHERE chatid=?",(message.chat.id,))
		song = cursor.fetchone()[0]
		await bot.send_message(message.chat.id, f"{name}\nПесня: {song}\nОстальное пока в разработке")
	except Exception as e:
		await bot.send_message(message.chat.id, "В этом чате нет коллаба!")
		print(e)
		
@bot.message_handler(commands=["closecollab"])
async def closecollab(message):
	try:
		cursor.execute("DELETE FROM collabs WHERE chatid=?",(message.chat.id,))
		conn.commit()
		await bot.send_message(message.chat.id, "Коллаб удалён!")
	except Exception as e:
		await bot.send_message(message.chat.id, "В этом чате нету коллаба!")

@bot.message_handler(commands=["support"])
async def support(message):
	question = ' '.join(message.text.split()[1:])
	try:
		if message.text.split()[1] != None:
			await bot.send_message(-1002778968248, f"Пользователь [{message.from_user.username}](tg://user?id={message.from_user.id}) \\(id\\={message.from_user.id}\\) спросил: \n{question}", parse_mode="MarkdownV2")
			await bot.send_message(message.chat.id, "Вопрос отправлен, ждите ответ.")
	except Exception as e:
		await bot.send_message(message.chat.id, "Использование команды: \n/support <вопрос>")
	
@bot.message_handler(commands=["respond"])
async def respond(message):
	user_id = ''.join(message.text.split()[1])
	print(user_id)
	answer = ' '.join(message.text.split()[2:])
	await bot.send_message(user_id, f"Вам пришёл ответ: \n{answer}")

@bot.message_handler(commands=['compilerust'])
async def compilerust(message):
	code = ' '.join(message.text.split()[1:])
	print(code)
	if len(code) > 1:
		async with aiohttp.ClientSession() as sess:
			headaches = {
			"User-Agent": "PythonScript/1.0",
			"Content-Type": "application/json",
			"Accept": "application/json"
			}
			async with sess.post(
				url="https://play.rust-lang.org/execute",
				headers=headaches,
				json={"channel": "stable",
 	   		"mode": "debug",
    			"crateType": "bin",
    			"tests": False,
    			"code": code,
    			"backtrace": False,
   	 		"edition": "2021"}
			) as resp:
				if resp.status == 200:
					result = await resp.json()
					await bot.send_message(message.chat.id, f"Вывод: {result['stdout']} \nStackrace:\n {result['stderr']}")
				else:
					await bot.send_message(message.chat.id, "ошибочка")

@bot.message_handler(commands=["sl","searchlevels"])
async def sl(message):
	query = ''.join(message.text.split()[1])
	try:
		if message.text.startswith("/sl"):
			url = f"https://gdbrowser.com/api/search/{query}"
		
			headers = {
			"User-Agent": "Geometry Dash/2.2 (iOS 15.6)",
			"Accept": "application/json",
			"Referer": "https://gdbrowser.com/"
			}
			async with aiohttp.ClientSession() as sess:
				async with sess.get(url=url,headers=headers) as resp:
					markup = types.InlineKeyboardMarkup()
					buttons = []
					data = await resp.json()
					for i in data[0:]:
						buttons.append(types.InlineKeyboardButton(text=f"{i['name']} от {i['author']}", url=f"https://gdbrowser.com/search/{i['id']}"))
					for i in range(0, len(buttons), 2):
						markup.row(*buttons[i:i+2])
					await bot.send_message(message.chat.id, "Результаты: ", reply_markup=markup)
					
	except Exception as e:
		await bot.send_message(message.chat.id, "Ничего не найдено.")
		print(e)
		
@bot.inline_handler(lambda query: len(query.query) > 0)
async def handle_inline(query: types.InlineQuery):
	try:
		search_query = query.query
		async with aiohttp.ClientSession() as sess:
			async with sess.get(url=f"https://gdbrowser.com/api/search/{search_query}") as resp:
				levels = []
				data = await resp.json()
				for i in data:
					name = i['name']
					author = i['author']
					difficulty = i['difficulty']
					desc =i['difficulty']
					stars = i['stars']
					orbs = i['orbs']
					downloads =i['downloads']
					likes = i['likes']
					length = i['length']
					coins = i['coins']
					songName =i['songName']
					songAuthor = i['songAuthor']
					
					levels.append(types.InlineQueryResultArticle(
			id=f"{name}",title = f"{name}",input_message_content=types.InputTextMessageContent(f"{name}\nот {author}\nСложность: {difficulty}\nЗвёзды: {stars}\nОписание: {desc}\nКол-во орбов: {orbs}\nЗагрузки: {downloads}\nЛайков: {likes}\nВремя: {length}\nМонет: {coins}\nНазвание песни: {songName}\nАвтор песни: {songAuthor}"),
			description=f"От {author}",
			thumbnail_url=f"https://levelthumbs.prevert.me/thumbnail/{i['id']}"
			))
		await bot.answer_inline_query(query.id, levels,cache_time=60)
	except NotADirectoryError as e:
		print(e)

@bot.message_handler(commands=["slbi","searchlevelbyid"])
async def slbi(message):
	try:
		id = ''.join(message.text.split()[1])
		async with aiohttp.ClientSession() as sess:
			headaches = {
				"User-Agent": "PythonScript/1.0",
				"Content-Type": "application/json",
				"Accept": "application/json"
			}
			async with sess.get(
				url=f"https://gdbrowser.com/api/search/{id}", headers=headaches) as resp:
					data = await resp.json()
					name = data[0]['name']
					author = data[0]['author']
					difficulty = data[0]['difficulty']
					desc = data[0]['difficulty']
					stars = data[0]['stars']
					orbs = data[0]['orbs']
					downloads = data[0]['downloads']
					likes = data[0]['likes']
					length = data[0]['length']
					coins = data[0]['coins']
					songName = data[0]['songName']
					songAuthor = data[0]['songAuthor']
					#выводим данные
					await bot.send_message(message.chat.id, f"{name}\nот {author}\nСложность: {difficulty}\nЗвёзды: {stars}\nОписание: {desc}\nКол-во орбов: {orbs}\nЗагрузки: {downloads}\nЛайков: {likes}\nВремя: {length}\nМонет: {coins}\nНазвание песни: {songName}\nАвтор песни: {songAuthor}")
	except Exception as e:
		await bot.send_message(message.chat.id, "Ничего не найдено.")
		print(e)
		
@bot.message_handler(commands=["daily"])
async def daily(message):
	async with aiohttp.ClientSession() as sess:
		async with sess.get(url="https://gdbrowser.com/daily") as resp:
			soup = BeautifulSoup(await resp.text(), 'html.parser')
			name = soup.find_all('h1')[0].text
			number = soup.find_all('h1')[1].text
			diff = soup.find_all('h1')[2].text
			stars = soup.find_all('h1')[3].text
			downloads = soup.find_all('h1')[5].text
			likes = soup.find_all('h1')[6].text
			length = soup.find_all('h1')[7].text
			await bot.send_message(message.chat.id, f"{name} ({number})\nСложность: {diff}\nЗвёзд: {stars}\nЗагрузок: {downloads}\nЛайков: {likes}\nДлина: {length}")

@bot.message_handler(commands=["base64encode","b64e"])
async def encodebase64(message):
	to_encode = ' '.join(message.text.split()[1:])
	encoded = base64.b64encode(to_encode.encode())
	await bot.send_message(message.chat.id, encoded)
	
@bot.message_handler(commands=["base64decode","b64d"])
async def decodebase64(message):
	to_decode = base64.b64decode(' '.join(message.text.split()[1:]))
	decoded = to_decode.decode('utf-8')
	await bot.send_message(message.chat.id, decoded)
	
@bot.message_handler(commands=["addmod"])
async def addmod(message: types.Message):
	admin = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
	status = admin.status in ["administrator","creator"]
	if status == True or message.from_user.id == 2100626507:
		level = int(message.text.split()[1])
		if level not in ADMIN_LEVELS: return
		admcur.execute("INSERT INTO admins(chatid, userid, level) VALUES (?,?,?)",(message.chat.id, message.reply_to_message.from_user.id, int(level)))
		admins.commit()
		await bot.send_message(message.chat.id, f"Поздравляем @{message.reply_to_message.from_user.username} со становление модератором {level} уровня!")
	else:
		await bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["mute"])
async def mute(message: types.Message):
	try:
		admin = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
		status = admin.status in ["administrator","creator"]
		admcur.execute("SELECT level FROM admins WHERE chatid=? AND userid=?",(message.chat.id, message.from_user.id))
		level = admcur.fetchone()
		level = level[0]
		print(level)
		if level >= 1 or status == True or message.from_user.id == 2100626507:
			user_to_mute = message.reply_to_message.from_user.id
			user_name = message.reply_to_message.from_user.username
			mute_time = int(message.text.split()[1]) * 60
			await bot.restrict_chat_member(message.chat.id, user_to_mute, until_date=datetime.now() + timedelta(seconds=mute_time))
			await bot.send_message(message.chat.id, f"Пользователь @{user_name} лишён права голоса на {int(mute_time / 60)} минут.\nМодератор: @{message.from_user.username}")
			await asyncio.sleep(mute_time)
			await bot.send_message(message.chat.id, f"@{user_name}, ваш срок молчания окончен.")
	except IndexError:
		await bot.send_message(message.chat.id, "Использованте команды:\n/mute <время в минутах>")
	except Exception as e:
		print(e)
		await bot.send_message(message.chat.id,"Недостаточно прав.")
		
@bot.message_handler(commands=["unmute"])
async def unmute(message: types.Message):
	try:
		admin = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
		status = admin.status in ["administrator","creator"]
		admcur.execute("SELECT level FROM admins WHERE chatid=? AND userid=?",(message.chat.id, message.from_user.id))
		level = admcur.fetchone()
		level = level[0]
		print(level)
		if level >= 1 or status == True or message.from_user.id == 2100626507:
			user_to_mute = message.reply_to_message.from_user.id
			user_name = message.reply_to_message.from_user.username
			await bot.restrict_chat_member(message.chat.id, user_to_mute, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
			await bot.send_message(message.chat.id, f"Пользователю @{user_name} вернули право голоса.\nМодератор: @{message.from_user.username}")
	except Exception as e:
		print(e)
		await bot.send_message(message.chat.id,"Недостаточно прав.")
		
@bot.message_handler(commands=["kick"])
async def kick(message:types.Message):
	try:
		admin = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
		status = admin.status in ["administrator","creator"]
		admcur.execute("SELECT level FROM admins WHERE chatid=? AND userid=?",(message.chat.id, message.from_user.id))
		level = admcur.fetchone()
		level = level[0]
		print(level)
		if level >= 2 or status == True or message.from_user.id == 2100626507:
			user_to_kick = message.reply_to_message.from_user.id
			user_name = message.reply_to_message.from_user.username
			await bot.kick_chat_member(message.chat.id, user_id=user_to_kick)
			await bot.send_message(message.chat.id, f"Пользователь @{user_name} был исключён.\nМодератор: @{message.from_user.username}")
	except Exception as e:
		await bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["unban"])
async def unban(message:types.Message):
	try:
		admin = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
		status = admin.status in ["administrator","creator"]
		admcur.execute("SELECT level FROM admins WHERE chatid=? AND userid=?",(message.chat.id, message.from_user.id))
		level = admcur.fetchone()
		level = level[0]
		print(level)
		if level == 3 or status == True or message.from_user.id == 2100626507:
			username = message.reply_to_message.from_user.usernameb
			
			await bot.unban_chat_member(message.chat.id, user_id=message.reply_to_message.from_user.id)
			await bot.send_message(message.chat.id, f"Пользователь @{username} был разбанен.\nМодератор: @{message.from_user.username}")
	except:
		await bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["ban"])
async def ban(message:types.Message):
	try:
		admin = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
		status = admin.status in ["administrator","creator"]
		admcur.execute("SELECT level FROM admins WHERE chatid=? AND userid=?",(message.chat.id, message.from_user.id))
		level = admcur.fetchone()
		level = level[0]
		print(level)
		if level == 3 or status == True or message.from_user.id == 2100626507:
			username = message.reply_to_message.from_user.username
			await bot.ban_chat_member(message.chat.id, user_id=message.reply_to_message.from_user.id)
			await bot.send_message(message.chat.id, f"Пользователь @{username} был забанен.\nМодератор: @{message.from_user.username}")
	except:
		await bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["warn"])
async def warn(message:types.Message):
	try:
		admin = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
		status = admin.status in ["administrator","creator"]
		admcur.execute("SELECT level FROM admins WHERE chatid=? AND userid=?",(message.chat.id, message.from_user.id))
		level = admcur.fetchone()
		level = level[0]
		print(level)
		if level == 3 or status == True or message.from_user.id == 2100626507:
			await bot.send_message(message.chat.id, f"Пользователю @{message.reply_to_message.from_user.username} выдано предупреждение.\nМодератор: @{message.from_user.username}")
	except:
		await bot.send_message(message.chat.id, "Недостаточно прав.")

@bot.message_handler(commands=["help","h"])
async def help(message):
	await bot.send_message(message.chat.id, "*Помощь по боту* \n_/mute_ \\<время мута\\> \\- мутит пользователя на заданное время в минутах \n_/unmute_ \\- выводит пользователя из мута \n_/ban_ \\- банит пользователя \n_/unban_ \\- разбанивает пользователя \n_/warn_ \\- выдаёт предупреждение пользователю \n_/kick_ \\- выгнать пользователя \n_/sl_ \\<название\\> \\- Ищет уровни по запросу в Geometry Dash\n_/slbi_ \\<id уровня\\> \\- Ищет уровень по ID в Geometry Dash \n_/sl_ \\<запрос\\> \\- Ищет уровни по запросу в Geometry Dash \n_/base64encode_ \\<строка\\> \\- Энкодирует строку в Base64 \n_/base64decode_ \\<строка\\> \\- Декодирует Base64 \n_/enrandomjoke_ \\- Выводит случайную шутку на английском \n_/writerules_ \\- перезаписывает правила чата \n_/readrules_ \\- показывает правила чата \n_/compilerust_ \\<код на rust\\> \\- компилирует введённый код на Rust", parse_mode="MarkdownV2")
	
@bot.message_handler(commands=["hug"])
async def hug(message):
	try:
		await bot.send_message(message.chat.id, f"@{message.from_user.username} обнял @{message.reply_to_message.from_user.username}")
	except:
		await bot.send_message(message.chat.id, "Вы должны ответить на сообщение командой!")
		
@bot.message_handler(commands=["kiss"])
async def kiss(message):
	try:
		await bot.send_message(message.chat.id, f"@{message.from_user.username} поцеловал @{message.reply_to_message.from_user.username}")
	except:
		await bot.send_message(message.chat.id, "Вы должны ответить на сообщение командой!")
		
@bot.message_handler(commands=["kill"])
async def kill(message):
	try:
		await bot.send_message(message.chat.id, f"@{message.from_user.username} убил @{message.reply_to_message.from_user.username}")
	except Exception as e:
		await bot.send_message(message.chat.id, "Вы должны ответить на сообщение командой!")
		print(e)
		
@bot.message_handler(commands=["fuck"])
async def fuck(message):
	try:
		await bot.send_message(message.chat.id, f"@{message.from_user.username} 'занялся любовью' с @{message.reply_to_message.from_user.username}")
	except Exception as e:
		await bot.send_message(message.chat.id, "Вы должны ответить на сообщение командой!")
		print(e)
	

		
@bot.message_handler(commands=["startstory"])
async def makestory(message):
	stcur.execute("INSERT INTO stories (chatid, content, active) VALUES (?,?,?) ON CONFLICT (chatid) DO UPDATE SET content = content + ?")
	length = message.text.split()[1:]
	title = " ".join(message.text.split()[2:])
	await bot.send_message(message.chat.id, f"Теперь каждое сообщение в этом чате будет добавлено в рассказ {title}")
		
@bot.message_handler(commands=["readrules","rr"])
async def readrules(message):
	with open(f"{message.chat.id}.rles","r") as f:
		rules = f.read()
		await bot.send_message(message.chat.id, rules)
		
@bot.message_handler(commands=["writerules","wr"])
async def writerules(message):
	rules = message.reply_to_message.text
	print(rules)
	with open(f"{message.chat.id}.rles","w") as rulef:
		
		rulef.write(f"{rules}")
	await bot.send_message(message.chat.id, "Правила обновлены.")
	
		
@bot.message_handler(commands=["enrandomjoke","enrj"])
async def randomjoke(message):
	joke = pyjokes.get_joke()
	await bot.send_message(message.chat.id, joke)
	
@bot.message_handler(commands=['r34'])
async def rule34(message):
	print(message.text.split())
	if message.chat.type == "private":
		async with pyrule34.AsyncRule34() as r34:
			get_random_post = await r34.search(tags=message.text.split()[1:], limit=5)
			for i in get_random_post:
				print(str(i).split()[1].replace("'","").replace(",",""))
				await bot.send_photo(message.chat.id, str(i).split()[1].replace("'","").replace(",",""))
	else:
		await bot.send_message(message.chat.id, "Команда доступна только в ЛС!")
		
@bot.message_handler(commands=["work"])
async def work(message: types.Message):
	try:
		balcur.execute("SELECT abletowork FROM coins WHERE userid = ?", (message.from_user.id,))
		abletowork = balcur.fetchone()
		abletowork =abletowork[0]
		if abletowork == 1:
			user_id = message.from_user.id
			gems = random.randint(30,99)
			balcur.execute("INSERT INTO coins (userid, coins, abletowork) VALUES (?,?,?) ON CONFLICT (userid) DO UPDATE SET coins = coins + ?",(user_id, gems, 0, gems))
			balances.commit()
			await bot.send_message(message.chat.id, f"Вы заработали {gems} кофекоинов")
			await asyncio.sleep(3600)
			balcur.execute("INSERT INTO coins (userid, coins, abletowork) VALUES (?,?,?) ON CONFLICT (userid) DO UPDATE SET abletowork = 1",(user_id, gems, 1))
			balances.commit()
		elif abletowork == 0:
			await bot.send_message(message.chat.id, "Отдохните, ёмаё")
	except:
		gems = random.randint(30,99)
		user_id = message.from_user.id
		balcur.execute("INSERT INTO coins (userid, coins, abletowork) VALUES (?,?,?) ON CONFLICT (userid) DO UPDATE SET coins = coins + ?",(user_id, gems, 0, gems))
		balances.commit()
		await bot.send_message(message.chat.id, f"Вы заработали {gems} кофекоинов")
		await asyncio.sleep(3600)
		balcur.execute("INSERT INTO coins (userid, coins, abletowork) VALUES (?,?,?) ON CONFLICT (userid) DO UPDATE SET abletowork = 1",(user_id, gems, 1))
		balances.commit()
	
		
@bot.message_handler(commands=["balance"])
async def balance(message: types.Message):
	user_id = message.from_user.id
	try:
		balcur.execute("SELECT coins FROM coins WHERE userid = ?",(user_id,))
		gems = balcur.fetchall()
		gems = gems[0][0]
		await bot.send_message(message.chat.id, f"Ваш баланс: {gems}")
	except Exception as e:
		print(e)
		await bot.send_message(message.chat.id, "У вас 0 кофекоинов")
		
@bot.message_handler(commands=["casino"])
async def kazik(message: types.Message):
	print(message.text.split()[1])
	to_dep = int(message.text.split()[1])
	if to_dep == None: await bot.send_message(message.chat.id, "Использование команды:\n/casino <сумма денег>ьл")
	userid=message.from_user.id
	balcur.execute("SELECT abletowork FROM coins WHERE userid=?",(userid,))
	abletowork = balcur.fetchone()
	abletowork = abletowork[0]
	print(abletowork)
	balcur.execute("SELECT coins FROM coins WHERE userid=?",(userid,))
	bal = balcur.fetchone()
	bal = bal[0]
	print(bal)
	if bal == 0 or to_dep > bal:
		await bot.send_message(message.chat.id, "У вас недостаточно денег!")
	else:
		isdouble = random.randint(0,1)
		if isdouble == 0:
			balcur.execute("INSERT INTO coins (userid, coins, abletowork) VALUES (?,?,?) ON CONFLICT (userid) DO UPDATE SET coins = coins - ?",(userid, bal - to_dep, abletowork, to_dep))
			balances.commit()
			await bot.send_message(message.chat.id, "Вы проиграли!")
		else:
			balcur.execute("INSERT INTO coins (userid, coins, abletowork) VALUES (?,?,?) ON CONFLICT (userid) DO UPDATE SET coins = coins + ?",(userid,bal + to_dep, abletowork, to_dep))
			balances.commit()
			await bot.send_message(message.chat.id, "Вы выиграли!")
		
@bot.message_handler(commands=["nahuiirisa"])
async def nahuiirisa(message):
	await irishuina(message.chat.id)
	
@bot.message_handler(func=lambda message: True,chat_types=["group","supergroup"])
async def respondai(message: types.Message):
	prompt = message.text.lower()
	print(prompt)
	
	if prompt.startswith('/'): return
	
	if prompt == "бот":
		await bot.send_message(message.chat.id, "здесь")
	
	if prompt == "что с ботом":
		await bot.send_message(message.chat.id, "да всё ок вроде")
		
	if message.from_user.is_bot == True:
		await bot.send_message(message.chat.id, "иди нахуй")
	"""
	await bot.send_chat_action(message.chat.id, 'typing')
	
	payload = {
		"inputs": f"<SC6>ты должен отвечать максимально коротко, разговаривать как 14 летний без молодёжного слэнга,с маленькой буквы и без знаков препинания, запрос: {prompt}</s>",
		"parameters":{
			"max_new_tokens": 500,
			"temperature": 0.7
		}
	}
	
	try:
		response = await asyncio.to_thread(
			requests.post,
			MODEL_API_URL,
			headers=HEADERS,
			json=payload
		)
		if response.status_code == 200:
			ai_response = response.json()[0]['generated_text'].split('</s>')[-1].split('SC6>')[1]
		else:
			ai_response = "скоро"
			print(response.status_code)
		await bot.send_message(message.chat.id, ai_response)
	except Exception as e:
		await bot.send_message(message.chat.id, f"что то пошло не так: {e}")"""
	
async def main():
	await bot.infinity_polling(allowed_updates=["message","inline_query"])
	
	
asyncio.run(main())
