import os, time, app, traceback
from datetime import datetime, timedelta
import sqlite3
informing = 15
INFORMING = 720
quitting = 45
QUITTING = 1440

informing_mes = "🖥Hệ thống: Đoạn chat sẽ tự động kết thúc nếu một trong hai người không nhắn trong vòng 45 phút. Để tăng khoảng thời gian đó lên 24h, các bạn hãy dùng lệnh /keep."
INFORMING_MES = "🖥Hệ thống: Đoạn chat sẽ tự động kết thúc trong vòng 12 tiếng sắp tới. Lưu ý rằng nếu một trong hai người không tương tác trong vòng 24h, đoạn chat sẽ tự động kết thúc."
quitting_mes = "🖥Hệ thống: Thời gian chờ đã hết (45 phút). Cuộc trò chuyện sẽ tự động kết thúc"
QUITTING_mes = "🖥Hệ thống: Thời gian chờ đã hết (24 giờ). Cuộc trò chuyện sẽ tự động kết thúc"
LOG = "log.txt"

db = sqlite3.connect("storage/user.db", check_same_thread=False)
user = db.cursor()

def autoend():
    while True:
        try:
            user.execute("SELECT * FROM users")
            db.commit()
            list = user.fetchall()
            cur = datetime.now()
            a = []
            b = []
            for num in range(0, len(list), 2):
                item = [list[num], list[num + 1]]
                t1 = datetime.strptime(item[0][2].strip(), "%m/%d/%Y, %H:%M:%S")
                t2 = datetime.strptime(item[1][2].strip(), "%m/%d/%Y, %H:%M:%S")
                t = min(t1, t2)
                if t + timedelta(minutes=INFORMING) > cur and int(item[0][3] == 1):
                    continue
                elif t + timedelta(minutes=informing) > cur and int(item[0][3] == 0):
                    continue
                if int(item[0][3]) == 1:
                    if t + timedelta(minutes=QUITTING) < cur:
                        a.extend([item[0][0], item[0][1]])
                        b.extend([QUITTING_mes, QUITTING_mes])
                        kill(item[0][0], item[0][1])
                    elif cur - t - timedelta(minutes=INFORMING) < timedelta(minutes=1):
                        a.extend([item[0][0], item[0][1]])
                        b.extend([INFORMING_MES, INFORMING_MES])
                elif int(item[0][3]) == 0:
                    if t + timedelta(minutes=quitting) < cur:
                        a.extend([item[0][0], item[0][1]])
                        b.extend([quitting_mes, quitting_mes])
                        kill(item[0][0], item[0][1])
                    elif cur - t - timedelta(minutes=informing) < timedelta(minutes=1):
                        a.extend([item[0][0], item[0][1]])
                        b.extend([informing_mes, informing_mes])
            app.send_texts(a, b)
        except Exception:
            errnum = traceback.format_exc()
            cur = datetime.now()
            cur = cur.strftime("%m/%d/%Y, %H:%M:%S")
            f = open("log.txt", 'a+', encoding='utf-8')
            f.write(cur + '\n')
            f.write(errnum + '\n\n\n')
            f.close()
        time.sleep(60)


#add row
def add(recipient_id, matching_id, default=0):
    cur = datetime.now()
    last_message = cur.strftime("%m/%d/%Y, %H:%M:%S")
    data = [(recipient_id, matching_id, last_message, default)]
    print(data)
    user.executemany("INSERT INTO users VALUES (?,?,?,?)", data)
    db.commit()

#update row
def update(recipient_id, keep=0):
    cur = datetime.now()
    cur = cur.strftime("%m/%d/%Y, %H:%M:%S")
    if keep:
        user.execute(f"""UPDATE users SET last_message = '{cur}', keep = 1
    WHERE id = {recipient_id}""")
    else:
        user.execute(f"""UPDATE users SET last_message = '{cur}'
    WHERE id = {recipient_id}""")
    db.commit()

#delete row
def delete(recipient_id):
    user.execute(f"DELETE from users WHERE id = {recipient_id}")
    db.commit()

#check if a user exists
def get(recipient_id):
    user.execute(f"SELECT * FROM users WHERE id = {recipient_id}")
    db.commit()
    list = user.fetchall()
    if (len(list)):
        return list[0][1]
    return ""

#stop a conversation
def kill(a, b):
    delete(a)
    delete(b)

#set converation between a and b kept
def keep(a, b):
    update(a, 1)
    update(b, 1)

#match 2 users
def match(a, b):
    add(a, b)
    add(b, a)

#get all user ids
def all():
    user.execute("SELECT id FROM users")
    db.commit()
    res = user.fetchall()
    for i in range(0, len(res)):
        res[i] = res[i][0]
    return res

#write to log
def fetch():
    user.execute("SELECT * FROM users")
    list = user.fetchall()
    f = open("storage/database.txt", "w", encoding="utf-8")
    message = ""
    data = []
    for i in list:
        for j in i:
            f.write(str(j) + " ")
            message += str(j) + " "
        f.write('\n')
        message += '\n'
        if len(message) >= 1900:
            message = ""
            data.append(message)
    f.close()
    db.commit()
    return data

