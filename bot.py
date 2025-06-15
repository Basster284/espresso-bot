import json
import telebot
import os
import datetime
import requests
import asyncio
import base64
import pyjokes
from googletrans import Translator
from bs4 import BeautifulSoup

url_rust = "https://play.rust-lang.org/execute"

with open("token.json") as f:
	json_token = json.load(f)['token']

bot = telebot.TeleBot(json_token)

@bot.message_handler(commands=["support"])
def support(message):
	question = ' '.join(message.text.split()[1:])
	try:
		if message.text.split()[1] != None:
			bot.send_message(-1002778968248, f"Пользователь [{message.from_user.username}](tg://user?id={message.from_user.id}) \\(id\\={message.from_user.id}\\) спросил: \n{question}", parse_mode="MarkdownV2")
			bot.send_message(message.chat.id, "Вопрос отправлен, ждите ответ.")
	except Exception as e:
		bot.send_message(message.chat.id, "Использование команды: \n/support <вопрос>")
	
@bot.message_handler(commands=["respond"])
def respond(message):
	 user_id = ''.join(message.text.split()[1])
	 print(user_id)
	 answer = ' '.join(message.text.split()[2:])
	 bot.send_message(user_id, f"Вам пришёл ответ: \n{answer}")

@bot.message_handler(commands=['compilerust'])
def compilerust(message):
	code = ' '.join(message.text.split()[1:])
	print(code)
	if len(code) > 1:
		payload = {
			"channel": "stable",
    		"mode": "debug",
    		"crateType": "bin",
    		"tests": False,
    		"code": code,
    		"backtrace": False,
    		"edition": "2021"
		}
		
		headers = {
			"User-Agent": "PythonScript/1.0",
			"Content-Type": "application/json",
			"Accept": "application/json"
		}
		
		try:
			response = requests.post(url_rust,data=json.dumps(payload),headers=headers)
			result = response.json()
			bot.send_message(message.chat.id, f"Вывод: \n{result.get('stdout','')}\nStackrace: \n{result.get('stderr','')}")
			
		except Exception as e:
			print(f"{e}")
			
@bot.message_handler(commands=["base64encode","b64e"])
def encodebase64(message):
	to_encode = ' '.join(message.text.split()[1:])
	encoded = base64.b64encode(to_encode.encode())
	bot.send_message(message.chat.id, encoded)
	
@bot.message_handler(commands=["base64decode","b64d"])
def encodebase64(message):
	to_decode = base64.b64decode(' '.join(message.text.split()[1:]))
	decoded = to_decode.decode('utf-8')
	bot.send_message(message.chat.id, decoded)
	
	
@bot.message_handler(commands=['mute', 'm'])
def mute(message):
	user_sender_id = message.from_user.id
	user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
	if user_status == "administrator" or user_status == "creator":
		args = message.text.split()[1:]
		if len(args) > 0:
			mute_time = int(message.text.split()[1])
			user_id = message.reply_to_message.from_user.id
			bot.restrict_chat_member(message.chat.id, user_id, until_date=datetime.datetime.now() + datetime.timedelta(mute_time*60))
			bot.send_message(message.chat.id, f"Пользователь @{message.reply_to_message.from_user.username} ушёл в таймаут на {mute_time} минут")
		else:
			bot.send_message(message.chat.id, "Использование команды: \n /mute <время в минутах>")
	else:
		bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["kick"])
def kick(message):
    user_sender_id = message.from_user.id 
    user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
    if user_status == "administrator" or user_status == "creator":
    	user_id = message.reply_to_message.from_user.id
    	bot.kick_chat_member(message.chat.id, user_id) 
    	bot.send_message(message.chat.id, f"Пользователь @{message.reply_to_message.from_user.username} кикнут.")
    else:
    	bot.send_message(message.chat.id, "Недостаточно прав.")
	
@bot.message_handler(commands=["unmute", "um"])
def unmute(message):
	user_sender_id = message.from_user.id
	user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
	if user_status == "administrator" or user_status == "creator":
		user_id = message.reply_to_message.from_user.id
		bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
		bot.send_message(message.chat.id, f"Пользователь @{message.reply_to_message.from_user.username} ушёл из таймаута")
	else:
		bot.send_message(message.chat.id, "Недостаточно прав.")
	
@bot.message_handler(commands=["ban","b"])
def ban(message):
	user_sender_id = message.from_user.id
	user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
	if user_status == "administrator" or user_status == "creator":
		user_id = message.reply_to_message.from_user.id
		bot.ban_chat_member(message.chat.id, user_id)
		bot.send_message(message.chat.id, "Пользователь @{message.reply_to_message.from_user.username} забанен.")
	else:
		bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["delete","del"])
def delete(message):
	user_sender_id = message.from_user.id
	user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
	if user_status == "administrator" or user_status == "creator":
		delmess = message.reply_to_message.id
		bot.delete_message(message.chat.id, delmess)
	else:
		bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["anounce"])
def anounce(message):
	user_sender_id = message.from_user.id
	user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
	if user_status == "administrator" or user_status == "creator":
		bot.delete_message(message.chat.id, message.id)
		anounce_text = ' '.join(message.text.split()[1:])
		print(anounce_text)
		bot.send_message(message.chat.id, f"Анонс от @{message.from_user.username}: \n{anounce_text}")
	else:
		bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["unban","ub"])
def unban(message):
	user_sender_id = message.from_user.id
	user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
	if user_status == "administrator" or user_status == "creator":
		user_id = message.reply_to_message.from_user.id
		bot.unban_chat_member(message.chat.id, user_id)
		bot.send_message(message.chat.id, f"Пользователь @{message.reply_to_message.from_user.username} разбанен.")
	else:
		bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["warn","w"])
def warn(message):
	user_sender_id = message.from_user.id
	user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
	if user_status == "administrator" or user_status == "creator":
		bot.send_message(message.chat.id, f"Пользователю @{message.reply_to_message.from_user.username} выдано предупреждение.")
	else:
		bot.send_message(message.chat.id, "Недостаточно прав.")
	
@bot.message_handler(commands=["help","h"])
def help(message):
	bot.send_message(message.chat.id, "*Помощь по боту* \n_/mute_ \\<время мута\\> \\- мутит пользователя на заданное время в минутах \n_/unmute_ \\- выводит пользователя из мута \n_/ban_ \\- банит пользователя \n_/unban_ \\- разбанивает пользователя \n_/bam_ \\- БАМит пользователя \n_/warn_ \\- выдаёт предупреждение пользователю \n_/kick_ \\- выгнать пользователя \n_/slbi_ \\<id уровня\\> \\- Ищет уровень по ID в Geometry Dash \n_/translate_ \\<текст\\> \\- Переводит введённый текст на русский язык \n_/base64encode_ \\<строка\\> \\- Энкодирует строку в Base64 \n_/base64decode_ \\<строка\\> \\- Декодирует Base64 \n_/enrandomjoke_ \\- Выводит случайную шутку на английском \n_/writerules_ \\- перезаписывает правила чата \n_/readrules_ \\- показывает правила чата \n_/compilerust_ \\<код на rust\\> \\- компилирует введённый код на Rust", parse_mode="MarkdownV2")
	
@bot.message_handler(commands=["hug"])
def hug(message):
	try:
		bot.send_message(message.chat.id, f"@{message.from_user.username} обнял @{message.reply_to_message.from_user.username}")
	except:
		bot.send_message(message.chat.id, "Вы должны ответить на сообщение командой!")
		
@bot.message_handler(commands=["kiss"])
def kiss(message):
	try:
		bot.send_message(message.chat.id, f"@{message.from_user.username} поцеловал @{message.reply_to_message.from_user.username}")
	except:
		bot.send_message(message.chat.id, "Вы должны ответить на сообщение командой!")
		
@bot.message_handler(commands=["kill"])
def kill(message):
	try:
		bot.send_message(message.chat.id, f"@{message.from_user.username}] убил @{message.reply_to_message.from_user.username}")
	except Exception as e:
		bot.send_message(message.chat.id, "Вы должны ответить на сообщение командой!")
		print(e)
	
@bot.message_handler(commands=["bam"])
def bam(message):
	user_sender_id = message.from_user.id
	user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
	if user_status == "administrator" or user_status == "creator":
		user_id = message.reply_to_message.from_user.id
		bot.send_message(message.chat.id, f"Пользователь [{message.reply_to_message.from_user.username}](tg://user?id={message.reply_to_message.from_user.id}) заБАМен\\.", parse_mode="MarkdownV2")
	else:
		bot.send_message(message.chat.id, "Недостаточно прав.")
		
@bot.message_handler(commands=["readrules","rr"])
def readrules(message):
	with open(f"{message.chat.id}.rles","r") as f:
		rules = f.read()
		bot.send_message(message.chat.id, rules)
		
@bot.message_handler(commands=["writerules","wr"])
def writerules(message):
	user_sender_id = message.from_user.id
	user_status = bot.get_chat_member(message.chat.id, user_sender_id).status
	if user_status == "administrator" or user_status == "creator":
		with open(f"{message.chat.id}.rles","w") as f:
			rules = message.reply_to_message.text
			f.write(f"{rules}")
			bot.send_message(message.chat.id, "Правила обновлены.")
	else:
		bot.send_message(message.chat.id, "Недостаточно прав.")

@bot.message_handler(commands=["searchlevelbyid","slbi"])
def searchlevelbyid(message):
	args = message.text.split()[1:]
	if len(args) > 0:
		levelid = args[0]
		try:
			url = f"https://gdbrowser.com/{levelid}"
			response = requests.get(url)
			response.raise_for_status()
	
			soup = BeautifulSoup(response.text, 'html.parser')
	
			title_tag = soup.find('title')
			level_name = title_tag.text.split('(')[0].strip() if title_tag else "Название не найдено"
	
			meta_desc = soup.find('meta', property='og:description')
			if meta_desc:
				content = meta_desc['content']
				data = {}
				for part in content.split('|'):
					part = part.strip()
					if ':' in part:
						key, value = part.split(':', 1)
						data[key.strip()] = value.strip()
		
				level_id = data.get('ID', '')
				difficulty = data.get('Difficulty', '')
				downloads = data.get('Downloads', '')
				likes = data.get('Likes', '')
				song_info = data.get('Song', '')
			else:
				level_id = soup.find('cy').text if soup.find('cy') else ''
			difficulty = soup.find(id='difficultytext').text if soup.find(id='difficultytext') else ''
	
			downloads_img = soup.find('img', src=lambda x: 'download.png' in x if x else False)
			likes_img = soup.find('img', id='likeImg')
		
			downloads = downloads_img.find_next_sibling('h1').text if downloads_img else ''
			likes = likes_img.find_next_sibling('h1').text if likes_img else ''
			song_info = ""

			if song_info:
				if '(' in song_info and ')' in song_info:
					song_name = song_info.split('(')[0].strip()
					song_id = song_info.split('(')[1].split(')')[0].strip()
				else:
					song_name = song_info
					song_id = ""
			else:
				song_name_tag = soup.find(id='songname')
				song_name = song_name_tag.text if song_name_tag else ""
		
				song_id_match = None
				song_info_tag = soup.find(id='songInfo')
				if song_info_tag:
					import re
					song_id_match = re.search(r'SongID: (\d+)', song_info_tag.text)
			
			song_id = song_id_match.group(1) if song_id_match else ""
			if level_name != "Level Search":
				thumbnail = f"https://levelthumbs.prevter.me/thumbnail/{level_id}"
				rthumb = requests.get(thumbnail)
				if rthumb.status_code == 404:
					bot.send_message(message.chat.id,f"*{level_name}* \nID\\: `{level_id}`\nСложность\\: {difficulty}\nЗагрузки\\: {downloads}\nЛайки\\: {likes}\nПесня\\: [{song_name}](http://www.newgrounds.com/audio/listen/{song_id})", parse_mode="MarkdownV2")
				else:
					bot.send_photo(message.chat.id, photo=thumbnail, caption=f"*{level_name}* \nID\\: `{level_id}`\nСложность\\: {difficulty}\nЗагрузки\\: {downloads}\nЛайки\\: {likes}\nПесня\\: [{song_name}](http://www.newgrounds.com/audio/listen/{song_id})", parse_mode="MarkdownV2")
			else:
				bot.send_message(message.chat.id, "Ничего не найдено.")
		except requests.exceptions.RequestException as e:
			print(f"Ошибка при запросе: {e}")
	else:
		bot.send_message(message.chat.id, "Использование команды: \n/slbi <id уровня>")
		
@bot.message_handler(commands=["enrandomjoke","enrj"])
def randomjoke(message):
	joke = pyjokes.get_joke()
	bot.send_message(message.chat.id, joke)

@bot.message_handler(commands=["translate","tr"])
def translate(message):
	translator = Translator()
	texttotranslate = ' '.join(message.text.split()[1:])
	bot.send_message(message.chat.id, f"Перевод: \n{translator.translate(texttotranslate,dest='ru').text}")
	
bot.infinity_polling()
