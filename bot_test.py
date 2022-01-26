import os
import telebot
import urllib
import json
from configparser import ConfigParser
from telebot import types
import Sentinela
from Sentinela import *
import threading
import time
from datetime import datetime
import asyncio
import concurrent.futures

#TODO usar SSIM index para filtrar as imagens antes da análise
#https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/

#TODO terminar de instalar opencv no raspberry. Parei no item 9, setup and build. https://www.pyimagesearch.com/2015/02/23/install-opencv-and-python-on-your-raspberry-pi-2-and-b/


#https://pythonrepo.com/repo/eternnoir-pyTelegramBotAPI-python-third-party-apis-wrappers

parser = ConfigParser()
parser.read('bot_sentinela.ini')
bot_name = parser.get('bot_config', 'bot_name')
bot_username = parser.get('bot_config', 'bot_username')
bot_url = parser.get('bot_config', 'bot_url')
bot_token =  parser.get('bot_token', 'token')
bot_users = parser.get('users','users_id').split(',')


flag = 0                    #flag para iniciar/parar vigilia
lock = threading.Lock()     #variavel lok
log_cam = dict()            #log_cam
mostrar_sempre = 0          #mostrar (1) ou não (0) varredura

target_classes = ['person', 'bicycle', 'car',
                       'motorcycle', 'bus', 'truck',
                       'bird', 'cat', 'dog', 'horse',
                       'sheep', 'cow', 'backpack', 'umbrella',
                       'handbag', 'sports ball', 'kite', 'bottle',
                       'knife', 'chair', 'cell phone']

bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['menu', 'start'])
def send_welcome(message):
    msg = ''' Sentinela bot
    Envie /i p.'''
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('/iniciar')
    itembtn2 = types.KeyboardButton('/parar')
    itembtn3 = types.KeyboardButton('/lixo')
    markup.add(itembtn1, itembtn2, itembtn3)
	# bot.reply_to(message, "Olá!")
    bot.send_message(message.chat.id, "Escolha uma opção:", reply_markup=markup)



@bot.message_handler(commands = ['greet'])
def greet(message):
    msg = ''' Hello, how are you? 
Send /meow to get a cat image.
Send /fact to get random Cat Fact.'''
    bot.send_message(message.chat.id, msg)

def del_uninterested_tags(tags):
    global target_classes
    aux = tags.copy()
    # print(aux)
    idx_del = []
    for idx , val in enumerate(aux):
        # print(val)
        if val not in target_classes:
            idx_del.append(idx)
    # print(idx_del)
    aux = [i for j, i in enumerate(aux) if j not in idx_del]
    return aux

def vigiando(message):
    global log_cam
    global lock
    global mostrar_sempre
    lock.acquire()
    flag = get_flag()
    lock.release()
    # print('Thread vigiando iniciada...')
    # print("Flag:", flag)
    sentinela = Sentinela()
    verify_change = dict()
    if flag:

        # print("flag dentro do while:", flag , id(flag))
        # print(threading.current_thread())
        for cam, img, class_tagged in sentinela.sentinela_fazendo_ronda():
            print(cam, class_tagged)
            if class_tagged:
                # print(log_cam)
                camera_id = str(list(cam.keys())[0])
                update_cam_history(camera_id,class_tagged,log_cam)
                print(log_cam)
                tags_dif = None



                if (len (log_cam[camera_id].keys()) == 1):
                    tags_dif = True
                    # aux = del_uninterested_tags(log_cam[camera_id]['tag0'])
                    # log_cam[camera_id]['tag0'] = aux
                if (len (log_cam[camera_id].keys()) > 1):
                    log_cam[camera_id]['tag1'] = del_uninterested_tags(log_cam[camera_id]['tag1'])
                    tags_dif = not (((log_cam[camera_id]['tag0']) == (log_cam[camera_id]['tag1'])) )
                print(log_cam, "tag_dif:", tags_dif)



                if (tags_dif or mostrar_sempre):

                    # bot.reply_to(message, "log_cam: "+ str(log_cam))
                    retval, buffer = cv2.imencode('.jpg', img)
                    jpg_as_text = base64.b64encode(buffer)
                    bot.send_photo(message.chat.id, buffer)
                    bot.reply_to(message, "Sentinela informa: " + "camera: " + str(camera_id) + " - tags: " + str(class_tagged) +
                                 " \n" + str(datetime.now()) +
                                 "\n" + "log_cam: "+ str(log_cam) )



def update_cam_history(cam, tag, log_cam):
    # cam = str(cam)
    if cam in log_cam.keys():
        if 'tag1' in log_cam[cam].keys():
            aux = log_cam[cam]['tag1']
            log_cam[cam]['tag0'] = log_cam[cam]['tag1']
            log_cam[cam]['tag1'] = tag
        else:
            log_cam[cam]['tag1'] = tag

    else:
        log_cam[cam] = {'tag0': tag}

    return log_cam


def get_flag():
    global flag
    # print("Dentro de get_flag()")
    return flag

def toggle_flag():
    global lock
    lock.acquire()
    global flag
    if flag == 1:

        flag = 0
    else:
        flag = 1
    lock.release()
    return  flag
    # print("Dentro de toggle_flag()", flag, id(flag))



@bot.message_handler(commands=['iniciar', 'parar'])
def vigilia(message):
    global lock
    global flag
    # print(message.text)
    # print("Comando ",message, "recebido")

    if message.text == '/iniciar':
        print("Iniciando" )
        bot.send_message(message.chat.id, "------------------------------------------------------")
        bot.send_message(message.chat.id, "Iniciando vigilia..."+ str(datetime.now()))
        print(message)
        print(bot_users)
        global lock
        # lock.acquire()
        toggle_flag()
        # print("Valor fag em iniciar: ", flag)
        # lock.release()
        if flag:
            while True:
                vigiando(message)
                print("vigiando acionado!")
                if not get_flag():
                    break



    if message.text == '/parar':
        print("parando")
        bot.send_message(message.chat.id, "Parando vigilia...")
        # lock.acquire()
        toggle_flag()
        # print("Valor fag em parar: ", flag)
        # lock.release()



    # lock = threading.Lock()
    # x = threading.Thread(target=vigiando(message), args=(1,))
    # x.name = 'thread_vigiando'
    # x.start()
    # print("Threads ativas:",  threading.current_thread(), "Num threads: ", threading.active_count())
    # print("Iniciando Vigilia")








    # bot.reply_to(message, message.text)



# import timeit
#
# start = timeit.timeit()
# print("hello")
# bot.send_message("oi")
# end = timeit.timeit()
# print(end - start)


# print("Teste antes do polling")
try:

    bot.polling()
except:
    print("Erro de conexão com telegram")
# print("Teste")

