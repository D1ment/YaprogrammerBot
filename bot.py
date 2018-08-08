# -*- coding: utf-8 -*-
import time, os, sys
import eventlet
import requests
import logging
import telebot
import vk_api
from time import sleep
from telebot import types

# vk avtoriz
login = 'login'
password = 'pass'

# Переходим в рабочую директорию скрипта, независимо от места запуска
os.chdir(os.path.dirname(sys.argv[0]))

URL_VK = 'https://api.vk.com/method/wall.get?domain=CHENNEL&count=5&filter=owner'
FILENAME_VK = 'last_known_id.txt'
BASE_POST_URL = 'https://vk.com/CHENNEL?w=wall-49131654_'

BOT_TOKEN = 'TOKEN'
CHANNEL_NAME = '@chennel'
#CHANNEL_NAME = '@test_botmy'

bot = telebot.TeleBot(BOT_TOKEN)
hideBoard = types.ReplyKeyboardHide()

def get_data():
    timeout = eventlet.Timeout(10)
    try:
        feed = requests.get(URL_VK)
        return feed.json()
    except eventlet.timeout.Timeout:
        logging.warning('Got Timeout while retrieving VK JSON data. Cancelling...')
        return None
    finally:
        timeout.cancel()
		
def send_new_posts(items, last_id):
    for item in items:
        if item['id'] <= last_id:
            break
	if item['attachment']['type'] in ['photo', 'video']:
		
		text = item['text'].replace('<br><br>', '<br>')
		text_res = text[:text.find('<br>#')]
		text_res = text_res.replace('<br>', '\n\n') 
		tegi = text[text.find('#'):] 
		clean_text = text_res[:130] + '...' + '\n\n' + tegi	

		if item['attachment']['type'] == 'photo':
			imeg = item['attachment']['photo']['src_big']
			p = requests.get(imeg)
			out = open('img/img.jpg', 'wb')
			out.write(p.content)
			out.close()
		
		if item['attachment']['type'] == 'video':
			imeg = item['attachment']['video']['image_big']
			p = requests.get(imeg)
			out = open('img/img.jpg', 'wb')
			out.write(p.content)
			out.close()
		
		url = BASE_POST_URL + str(item['id'])
		#vk_session = vk_api.VkApi(login, password, number=None)
		#vk_session.vk_login()
                #vkin = vk_session.http.post('http://vk.com/cc', {'act': 'shorten', 'al': '1', 'link': url})
		#url_vk = vkin.text
		#urlnew = url_vk[url_vk.find('http://'):]
		urln = requests.get('https://clck.ru/--?url=' + url)
		urlnew = urln.content
		text = clean_text + '\n\n' + urlnew
		bot.send_photo(CHANNEL_NAME, open('img/img.jpg', 'rb'), caption=text)#, reply_markup=hideBoard)
	
        #bot.send_message(CHANNEL_NAME, text, disable_web_page_preview=false)
        time.sleep(1)
    return

def check_new_posts_vk():
    logging.info('[VK] Started scanning for new posts')
    with open(FILENAME_VK, 'rt') as file:
        last_id = int(file.read())
        if last_id is None:
            logging.error('Could not read from storage. Skipped iteration.')
            return
        logging.info('Last ID (VK) = {!s}'.format(last_id))
    try:
        feed = get_data()

        if feed is not None:
            entries = feed['response'][1:]
            try:
                tmp = entries[0]['is_pinned']
                send_new_posts(entries[1:], last_id)
            except KeyError:
                send_new_posts(entries, last_id)
            with open(FILENAME_VK, 'wt') as file:
                try:
                    tmp = entries[0]['is_pinned']
                    file.write(str(entries[1]['id']))
                    logging.info('New last_id (VK) is {!s}'.format((entries[1]['id'])))
                except KeyError:
                    file.write(str(entries[0]['id']))
                    logging.info('New last_id (VK) is {!s}'.format((entries[0]['id'])))
    except Exception as ex:
        logging.error('Exception of type {!s} in check_new_post(): {!s}'.format(type(ex).__name__, str(ex)))
        pass
    logging.info('[VK] Finished scanning')
    return
	
	
if __name__ == '__main__':
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s', level=logging.INFO,
                        filename='bot_log.log', datefmt='%d.%m.%Y %H:%M:%S')
    if 1 == 1:
        while True:
            check_new_posts_vk()
            logging.info('[App] Script went to sleep.')
            time.sleep(60 * 4)
    else:
        check_new_posts_vk()
    logging.info('[App] Script exited.\n')
