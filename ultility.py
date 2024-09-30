import requests, json, os, multiprocessing, pytube, time, copy
from bs4 import BeautifulSoup
import app, users, matching, config, traceback
from datetime import datetime
import sqlite3
DIR = os.path.abspath('music.txt')
DIR1 = os.path.abspath('musicurl.txt')
assets = {

}

ultility_db = sqlite3.connect("storage/ultility.db")
ultility_cursor = ultility_db.cursor()

music_url = sqlite3.connect("storage/musicurl.db")
musicurl = music_url.cursor()

def music(recipient_id, url):
    data = {
        'server' : config.debug,
        'type' : 1,
        'message' : url
    }
    url = "https://sonder-space1.p.rapidapi.com/"
    headers = {
    	"X-RapidAPI-Key": "ddbbf1b1d3mshefe9f7f72923950p1f78dfjsn3e61cd4be709",
    	"X-RapidAPI-Host": "sonder-space1.p.rapidapi.com",
    	"Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    response = response.json()
    while response.get('messages'):
        response = requests.post(url, json=data, headers=headers)
        response = response.json()
    if response['status'] == "error":
        app.send_text(recipient_id, response['message'])
        return
    other = matching.get(recipient_id)
    users.saves['audio']['message']['attachment']['payload']['attachment_id'] = response['id']
    users.saves['audio']['recipient']['id'] = recipient_id
    c = [copy.deepcopy(users.saves['audio'])]
    a = [recipient_id]
    b = ["Now playing: *" + response['title'] + "*"]
    if other:
        a.append(other)
        b = b * 2
        users.saves['audio']['recipient']['id'] = other
        c.append(users.saves['audio'])
    app.send_messages(c)
    app.send_texts(a, b)

def lyrics(message):
    try:
        search_url = "https://www.google.com/search?q=Lyrics " + message
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find("div", {"class":"hwc"})
        return content.text
    except:
        return ""

def run():
    while True:
        try:
            ultility_cursor.execute("SELECT * from queue")
            list = ultility_cursor.fetchall()
            ultility_db.commit()
            ultility_cursor.execute("DELETE from queue")
            ultility_db.commit()
            for item in list:
                if int(item[2]) == 1:
                    music(item[0], item[1])
        except Exception:
            errnum = traceback.format_exc()
            cur = datetime.now()
            cur = cur.strftime("%m/%d/%Y, %H:%M:%S")
            f = open("log.txt", 'a+', encoding='utf-8')
            f.write(cur + '\n')
            f.write(errnum + '\n\n\n')
            f.close()
        time.sleep(2)