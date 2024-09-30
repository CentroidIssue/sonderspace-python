from datetime import datetime, timedelta
import json, os, app
import matching, ultility, config
from youtubesearchpython import VideosSearch
import sqlite3, copy

ADMIN_ID = config.ADMIN_ID
saves = os.path.abspath('saves.json')
saves = json.load(open(saves, encoding="utf-8"))

adj = {
    "11" : ["11", "13"],
    "12" : ["21", "23"],
    "13" : ["11", "21", "23", "13"],
    "21" : ["12", "13"],
    "22" : ["22", "23"],
    "23" : ["22", "12", "13", "23"]
}

answering = {

}

active_users = {

}

cool_down = {

}

cool_down_music = {

}

whitelist = sqlite3.connect("storage/premium.db", check_same_thread=False)
wl = whitelist.cursor()

banlist = sqlite3.connect("storage/banlist.db", check_same_thread=False)
bl = banlist.cursor()

music_url = sqlite3.connect("storage/musicurl.db", check_same_thread=False)
musicurl = music_url.cursor()

ultility_db = sqlite3.connect("storage/ultility.db", check_same_thread=False)
ultility_cursor = ultility_db.cursor()

queue_db = sqlite3.connect("storage/queue.db", check_same_thread=False)
queue_cursor = queue_db.cursor()

def inqueue(recipient_id):
    for key in adj:
        queue_cursor.execute(f"SELECT * FROM '{key}' WHERE id = {int(recipient_id)}")
        list = queue_cursor.fetchall()
        queue_db.commit()
        if len(list):
            return key
    queue_cursor.execute(f"SELECT * FROM prom WHERE id = {int(recipient_id)}")
    list = queue_cursor.fetchall()
    queue_db.commit()
    if len(list):
        return "prom"
    return 0

def inform(text):
    textt = ""
    for i in range(1, len(text)):
        textt +=  text[i] + " "
    a = []
    b = []
    for recipient_id in matching.all():
        a.append(recipient_id)
        b.append(textt)
    for key in answering:
        a.append(key)
        b.append(textt)
    for key in adj:
        queue_cursor.execute(f"SELECT * FROM '{key}'")
        queue_db.commit()
        list = queue_cursor.fetchall()
        for item in list:
            a.append(item[0])
            b.append(textt)
    app.send_texts(a, b)

def help(recipient_id):
    app.send_texts([recipient_id, recipient_id], [saves['Guide'], saves['full command']])
    saves['how to use'].update({'recipient' : {'id' : recipient_id}})
    app.send_message(saves['how to use'])

def queue(recipient_id, type):
    recipient_id = int(recipient_id)
    if (inqueue(recipient_id)):
        app.send_text(recipient_id, saves['in queue'])
        return
    if matching.get(recipient_id) != '':
        app.send_text(recipient_id, saves['in chat'])
        return
    type = "".join(type)
    if type in ["11", "12", "13", "21", "22", "23"]:
        app.send_texts([recipient_id, recipient_id], [saves['donate'], saves['queuing']])
        if int(recipient_id) == 6433851309962620:
            matching.match(recipient_id, 0)
            app.send_text(recipient_id, saves['matching success'])
            return
        for x in adj[type]:
            queue_cursor.execute(f"SELECT * FROM '{x}' WHERE priority = (SELECT MIN(priority) FROM '{x}')")
            queue_db.commit()
            list = queue_cursor.fetchone()
            if list:
                opponent_id = list[0]
                queue_cursor.execute(f"DELETE FROM '{x}' WHERE id = {opponent_id}")
                queue_db.commit()
                matching.match(recipient_id, opponent_id)
                app.send_texts([recipient_id, opponent_id], [saves['matching success'], saves['matching success']])
                return
        queue_cursor.execute(f"SELECT MAX(priority) FROM '{type}'")
        queue_db.commit()
        maxx = copy.deepcopy(queue_cursor.fetchone())
        maxx = maxx[0]
        queue_cursor.execute(f"SELECT MIN(priority) FROM '{type}'")
        queue_db.commit()
        minn = copy.deepcopy(queue_cursor.fetchone())
        minn = minn[0]
        if maxx == None:
            maxx = 0
            minn = 2
        else:
            pass
        if str(recipient_id) in ADMIN_ID:
            queue_cursor.execute(f"INSERT INTO '{type}' VALUES (?, ?)", (recipient_id, minn - 1))
            queue_db.commit()
        else:
            queue_cursor.execute(f"INSERT INTO '{type}' VALUES (?, ?)", (recipient_id, maxx + 1))
            queue_db.commit()
    else:
        queue_cursor.execute(f"SELECT * FROM prom WHERE token = '{type}'")
        queue_db.commit()
        list = queue_cursor.fetchone()
        if not list:
            queue_cursor.execute(f"INSERT INTO prom VALUES (?, ?)", (recipient_id, type))
            queue_db.commit()
            app.send_texts([recipient_id, recipient_id], [saves['promming'], saves['donate']])
        elif list[0] == recipient_id:
            app.send_text(recipient_id, saves['in queue'])
            return
        else:
            token_delete(type)
            matching.add(recipient_id, list[0], 2)
            matching.add(list[0], recipient_id, 2)
            app.send_texts([recipient_id, list[0]], [saves['prommatch'], saves['prommatch']])
            app.send_texts([recipient_id, list[0]], [saves['info'], saves['info']])
            queue_cursor.execute(f"DELETE FROM prom WHERE token = '{type}'")
            queue_db.commit()

def end(recipient_id):
    if matching.get(recipient_id) == '' and not answering.get(recipient_id) and inqueue(recipient_id) == 0:
        app.send_text(recipient_id, saves['not in chat'])
        return 'error'
    if answering.get(recipient_id):
        answering.pop(recipient_id)
        get_started(recipient_id,forces=1)
        return 'success'
    if inqueue(recipient_id) != 0:
        app.send_text(recipient_id, saves['left queue'])
        x = inqueue(recipient_id)
        queue_cursor.execute(f"DELETE FROM '{x}' WHERE id = {recipient_id}")
        queue_db.commit()
        get_started(recipient_id,forces=1)
        return 'success'
    opponent_id = matching.get(recipient_id)
    matching.kill(recipient_id, opponent_id)
    app.send_texts([recipient_id, opponent_id], [saves['endingreq'], saves['ending']])
    get_started(recipient_id, forces=1)
    get_started(opponent_id, forces=1)
    return 'success'

def postback(recipient_id, postback):
    if postback['payload'] == "Start Chatting":
        if inqueue(recipient_id):
            app.send_text(recipient_id, saves['in queue'])
            return
        if matching.get(recipient_id) != '':
            app.send_text(recipient_id, saves['in chat'])
            return
        saves['gender1'].update({'recipient' : {'id' : recipient_id}})
        app.send_message(saves['gender1'])
    elif postback['payload'] == "Guide":
        help(recipient_id)
    elif postback['payload'] == "prom":
        app.send_text(recipient_id, saves['prom'])
    elif "youtube" in postback['payload']:
        command = [i for i in postback['payload'].split()]
        search_music(recipient_id, command)


def get_started(recipient_id, forces=0):
    if inqueue(recipient_id):
        app.send_text(recipient_id, saves['in queue'])
        return
    if matching.get(recipient_id) != "":
        app.send_text(recipient_id, saves['in chat'])
        return
    cur = datetime.now()
    if forces or (not active_users.get(recipient_id) or active_users[recipient_id] + timedelta(minutes=10) <= cur):
        saves['welcome'].update({'recipient' : {'id' : recipient_id}})
        app.send_message(saves['welcome'])
        active_users.update({recipient_id : cur})
        cool_down.update({recipient_id : cur})
    else:
        if cool_down[recipient_id] + timedelta(seconds=20) <= cur:
            app.send_text(recipient_id, saves['instruction'])
            cool_down.update({recipient_id : cur})

def quickrep(recipient_id, message):
    if message in ["True", "False"]:
        other = matching.get(recipient_id)
        if other == "":
            return
        if message == "True":
            app.send_texts([other, recipient_id], [saves['extended convo'], saves['extended convo']])
            matching.keep(other, recipient_id)
        else:
            app.send_texts([other, recipient_id], [saves['keep denied'], saves['keep denied']])
        return
    message = list(message)
    if ''.join(message) == '11':
        answering.update({recipient_id : message[1]})
        saves['gender2'].update({'recipient' : {'id' : recipient_id}})
        app.send_message(saves['gender2'])
    elif ''.join(message) == '12':
        answering.update({recipient_id : message[1]})
        saves['gender2'].update({'recipient' : {'id' : recipient_id}})
        app.send_message(saves['gender2'])
    elif ''.join(message) == '21':
        if not answering.get(recipient_id):
            app.send_text(recipient_id, saves['answering error'])
            get_started(recipient_id, 1)
            return
        message[0] = answering[recipient_id]
        answering.pop(recipient_id)
        queue(recipient_id, message)
    elif ''.join(message) == '22':
        if not answering.get(recipient_id):
            app.send_text(recipient_id, saves['answering error'])
            get_started(recipient_id, 1)
            return
        message[0] = answering[recipient_id]
        answering.pop(recipient_id)
        queue(recipient_id, message)
    elif ''.join(message) == '23':
        if not answering.get(recipient_id):
            app.send_text(recipient_id, saves['answering error'])
            get_started(recipient_id, 1)
            return
        message[0] = answering[recipient_id]
        answering.pop(recipient_id)
        queue(recipient_id, message)

def search_music(recipient_id, command):
    if len(command) < 3 or not command[1] in ['play', 'lyrics', 'search', 'clear']:
        app.send_text(recipient_id, saves['how to music'])
        return
    if command[1] == 'play':
        cur = datetime.now()
        if not recipient_id in ADMIN_ID and cool_down_music.get(recipient_id) and cool_down_music[recipient_id] + timedelta(seconds=10) > cur:
            app.send_text(recipient_id, "Mỗi người chỉ được gửi yêu cầu 1 lần trong 10 giây")
            return
        cool_down_music.update({recipient_id : cur})
        link = command[2]
        data = (recipient_id, link, 1)
        ultility_cursor.execute("INSERT INTO queue VALUES (?, ?, ?)", data)
        ultility_db.commit()
    elif command[1] == 'lyrics':
        q = ""
        for i in command[2:]:
            q = q + i + " "
        lyrics = ultility.lyrics(q)
        try:
            if lyrics == "":
                app.send_text(recipient_id, saves['cannot find lyrics'])
            else:
                lyrics = lyrics.splitlines()
                mes = ""
                for line in lyrics:
                    if len(mes + line) > 1900:
                        app.send_text(recipient_id, mes)
                        mes = line + "\n"
                    else:
                        mes = mes + line + "\n"
                app.send_text(recipient_id, mes)
        except:
            app.send_text(recipient_id, saves['cannot find lyrics'])
    elif command[1] == 'clear':
        musicurl.execute("DELETE from musicurl")
        music_url.commit()
    else:
        q = ""
        for i in command[2:]:
            q = q + i + " "
        search(recipient_id, q)

def search(recipient_id, q):
    other = matching.get(recipient_id)
    response = VideosSearch(q, limit=3).result()
    string = ""
    button = []
    for num, result in enumerate(response['result']):
        data = {
            "type": "postback",
            "title": "",
            "payload": ""
        }
        string = string +  "Id: " + str(num + 1) + "\n" + "Title: *" + result["title"] + "*\nUrl: youtube.com/watch?v=" + result['id'] + "\n\n"
        data.update({"title" : num + 1})
        data.update({"payload" : "/music play youtube.com/watch?v=" + result['id']})
        button.append(data)
    message1 = saves['music']
    message2 = saves['music_button']
    message1['message']['text'] = string
    message2['message']['attachment']['payload']['elements'][0]['buttons'] = button
    message1['recipient']['id'] = recipient_id
    message2['recipient']['id'] = recipient_id
    app.send_messages([message1, message2])
    if other:
        message1['recipient']['id'] = other
        app.send_message(message1)


def report(recipient_id, text):
    if (len(text) < 2):
        app.send_text(recipient_id, saves['how to report'])
    elif matching.get(recipient_id) == "":
        app.send_text(recipient_id, saves['in chat required'])
    else:
        textt = ""
        for i in range(1, len(text)):
            textt += text[i] + " "
        for admin in ADMIN_ID:
            app.send_text(admin, str(recipient_id) + " reported user " + str(matching.get(recipient_id)) + " for " + textt)
        app.send_text(recipient_id, saves['command executed'])

def keep(recipient_id):
    if matching.get(recipient_id) == "":
        app.send_text(recipient_id, saves['in chat required'])
        return
    other = matching.get(recipient_id)
    app.send_text(recipient_id, saves['keep sent'])
    saves['keep']['recipient']['id'] = other
    app.send_message(saves['keep'])
    return

def database(recipient_id, text):
    if len(text) < 2:
        app.send_text(recipient_id, saves['wrong syntax'])
        return
    if text[1] == 'fetch':
        message = matching.fetch()
        app.send_texts([recipient_id] * len(message), message)
        app.send_text(recipient_id, saves['command executed'])
    else:
        app.send_text(recipient_id, saves['wrong syntax'])

def is_banned(recipient_id):
    b = banlist.execute(f"SELECT * FROM ban WHERE id = {recipient_id}")
    banlist.commit()
    b = b.fetchall()
    return len(b)

def ban(recipient_id, text):
    if len(text) != 2:
        app.send_text(recipient_id, saves['wrong syntax'])
        return
    if (is_banned(text[1])):
        app.send_text(recipient_id, saves['already banned'])
        return
    data = [(int(text[1]), )]
    bl.executemany("INSERT INTO ban VALUES (?)", data)
    banlist.commit()
    other = matching.get(text[1])
    if other == "":
        return
    app.send_texts([recipient_id, other, text[1]], [saves['command executed'], saves["matching ban"], saves["ban message"]])
    matching.kill(other, text[1])


def unban(recipient_id, text):
    if len(text) != 2:
        app.send_text(recipient_id, saves['wrong syntax'])
        return
    if (is_banned(text[1]) == 0):
        app.send_text(recipient_id, saves['already unbanned'])
        return
    bl.execute(f"DELETE FROM ban WHERE id = {int(text[1])}")
    banlist.commit()
    app.send_text(recipient_id, saves['command executed'])

#check if the user is premium
def is_premium(recipient_id):
    w = whitelist.execute(f"SELECT * FROM premium WHERE id = {recipient_id}")
    whitelist.commit()
    w = w.fetchall()
    if len(w) == 0: return 0
    cur = datetime.now()
    expiry = datetime.strptime(w[0][1].strip(), "%m/%d/%Y, %H:%M:%S")
    # subscription expiry
    if expiry < cur:
        app.send_text(recipient_id, saves['premium expiry'])
        delpremium(recipient_id)
        return 0
    return expiry

#give premium
def premium(recipient_id, text):
    if len(text) != 3:
        app.send_text(recipient_id, saves['wrong syntax'])
        return
    if text[1] == "all":
        app.free_premium = 1
        app.send_text(recipient_id, saves['command executed'])
        return
    if (is_premium(text[1])):
        app.send_text(recipient_id, saves['already premium'])
        return
    cur = datetime.now()
    if (text[2] == 0): cur = cur + timedelta(weeks=1)
    else: cur = cur + timedelta(days=30)
    cur = cur.strftime("%m/%d/%Y, %H:%M:%S")
    data = [(int(text[1]), cur)]
    wl.executemany("INSERT INTO premium VALUES (?, ?)", data)
    whitelist.commit()
    app.send_texts([recipient_id, text[1]], [saves['command executed'], saves['premium']])


def delpremium(id):
    wl.execute(f"DELETE FROM premium WHERE id = {int(id)}")
    whitelist.commit()
#delete premium
def unpremium(recipient_id, text):
    if len(text) != 2:
        app.send_text(recipient_id, saves['wrong syntax'])
        return
    if text[1] == 'all':
        app.free_premium = 0
        app.send_text(recipient_id, saves['command executed'])
        return
    if (is_premium(text[1]) == 0):
        app.send_text(recipient_id, saves['already not premium'])
        return
    wl.execute(f"DELETE FROM premium WHERE id = {int(text[1])}")
    whitelist.commit()
    app.send_text(recipient_id, saves['command executed'])

def token_add(token):
    ultility_cursor.execute(f"INSERT INTO token VALUES (?)", (token, ))
    ultility_db.commit()

def token_delete(token):
    ultility_cursor.execute(f"DELETE FROM token WHERE value = '{token}'")
    ultility_db.commit()

def token(recipient_id, text):
    if (text[1] == 'add'):
        token_add(text[2])
    elif (text[1] == 'delete'):
        token_delete(text[2])
    else:
        app.send_text(recipient_id, saves['wrong syntax'])
        return
    app.send_text(recipient_id, saves['command executed'])
def prom8(recipient_id, text):
    if len(text) != 2:
        app.send_text(recipient_id, saves['wrong syntax'])
        return
    ultility_cursor.execute(f"SELECT * FROM token WHERE value = '{text[1]}'")
    list = ultility_cursor.fetchall()
    ultility_db.commit()
    if len(list) == 0:
        app.send_text(recipient_id, saves['token not found'])
        return
    queue(recipient_id, text[1])