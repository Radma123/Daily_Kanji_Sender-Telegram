import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import telebot
import logging
import os
import random

#настройка логгирования
logging.basicConfig(
    level=logging.WARNING,
    filename = "mylog.log",
    format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    )
logging.warning('________________________________HELLO__________________________________')


# настройки для телеги
token = os.environ['TOKEN']
channel_id = os.environ['CHANNEL_ID']
bot = telebot.TeleBot(token, parse_mode='HTML')


#фейк замена для браузера
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'Referer': 'https://www.google.com/'
}


def kanji_output():
    response = requests.get('https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B4%D0%B7%D1%91%D1%91-%D0%BA%D0%B0%D0%BD%D0%B4%D0%B7%D0%B8',headers=header).text
    soup = BeautifulSoup(response,'lxml')
    blocks = soup.find('table', {'class': 'sortable wikitable'})


    tds = random.choice(blocks.find_all('tr')[1:]).find_all('td')
    ru_translate = tds[-2].text
    kanji = tds[1].text


    # Создаем изображение---------------------------------
    width, height = 400, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Загружаем китайский шрифт (вам может понадобиться установить соответствующий шрифт)
    font = ImageFont.truetype("ARIALUNI.TTF", 325)

    # Рисуем символ на изображении
    draw.text((35, -25), text=kanji, fill='black', font=font)
    #------------------------------------------------------

    shirabe_req = requests.get(f'https://jisho.org/search/{kanji}%20%23kanji').text
    global to_er
    to_er = kanji
    shirabe_soup = BeautifulSoup(shirabe_req,'lxml')
    outp_telegram = []

    #meaning
    try:
        meaning = shirabe_soup.find('div',class_='kanji-details__main-meanings').text
        if meaning != []:
            outp_telegram.append(f'<b>{meaning.strip()}</b>')
        if ru_translate != None:
            outp_telegram.append(f'<b>{ru_translate.strip()}</b>\n')
    except:
        pass
    #Kun
    try:
        Kun = shirabe_soup.find(class_='dictionary_entry kun_yomi').find_all('a')
        txt_Kun = [i.text.replace(".","") for i in Kun]
        if txt_Kun != []:
            outp_telegram.append('<u>Kun:</u> '+', '.join(txt_Kun))
    except:
        pass
    #On
    try:
        On = shirabe_soup.find_all(class_='dictionary_entry on_yomi')[-1].find_all('a')
        txt_On = [i.text.replace(".","") for i in On]
        if txt_On != []:
            outp_telegram.append('<u>On:</u> '+', '.join(txt_On))
    except:
        pass

    #compounds
    try:
        row_comp = shirabe_soup.find('div',class_='row compounds')
        bullets = row_comp.find_all(class_ = 'small-12 large-6 columns')
        for bullet in bullets:
            pref = bullet.find('h2').text
            comps = bullet.find(class_='no-bullet').find_all('li')
            txt_comp = '<u>'+pref+':'+'</u>'+'\n'+'\n'.join([i.text.strip().replace('\n','').replace('  ',' ') for i in comps])
            if txt_comp != []:
                outp_telegram.append(txt_comp)
    except:
        pass

    #Отправка
    if len(''.join(outp_telegram))<=1023:
        text = '\n'.join(outp_telegram)
        bot.send_photo(chat_id=channel_id, photo=image, caption=text, disable_notification=False)
    else:
        to_send1 = outp_telegram[:len(outp_telegram)//2 + len(outp_telegram) % 2]
        to_send2 = outp_telegram[len(outp_telegram)//2 + len(outp_telegram) % 2:]
        text1 = '\n'.join(to_send1)
        text2 = '\n'.join(to_send2)
        bot.send_photo(chat_id=channel_id, photo=image, caption=text1, disable_notification=False)
        bot.send_message(chat_id=channel_id, text=text2, disable_notification=False)


if __name__ == '__main__':
    try:
        kanji_output()
    except Exception as err:
        logging.exception(str(err)+'\n'+'kanji: '+str(to_er))
        print('??????????????????___Fatal error has occured!___?????????????????',end='\n')
        print(err)
