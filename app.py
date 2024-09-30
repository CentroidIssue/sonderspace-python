import requests, traceback
from flask import Flask, request, render_template
import multiprocessing
from datetime import datetime
import config, users, matching, ultility
import os, json, valid
import aiohttp, asyncio
from urllib.parse import urlencode

ACCESS_TOKEN = config.PAGE_ACCESS_TOKEN
VERIFY_TOKEN = config.VERIFY_TOKEN
ADMIN_ID = config.ADMIN_ID
PAGE_ID = config.PAGE_ID
message_url = f"https://graph.facebook.com/v15.0/me/messages?access_token={ACCESS_TOKEN}"
app = Flask(__name__)
ATTACHMENTS = ['image', 'audio', 'video', 'file']
LOG = "log.txt"
maintenance = 0
process = 0
free_premium = 0

saves = os.path.abspath('saves.json')
saves = json.load(open(saves, encoding="utf-8"))

#main app, request receiving
@app.route("/", methods=['GET', 'POST'])
def recieve_method():
    global maintenance
    global process
    if request.method == 'GET':
        token = request.args.get("hub.verify_token")
        return verify_token(token)
    elif request.method == 'POST':
        requests.post(f"https://graph.facebook.com/me/subscribed_apps?access_token={ACCESS_TOKEN}", json={"subscribed_fields": ["messages", "messaging_postbacks", "messaging_optins", "messaging_optouts", "message_reads", "messaging_payments", "messaging_pre_checkouts", "messaging_checkout_updates", "messaging_account_linking", "messaging_referrals", "message_echoes", "messaging_game_plays", "standby", "messaging_handovers", "messaging_policy_enforcement", "message_reactions", "inbox_labels", "messaging_feedback"]})
        try:
            if process == 0:
                worker = multiprocessing.Process(target=ultility.run)
                worker.start()
                worker1 = multiprocessing.Process(target=matching.autoend)
                worker1.start()
                send_text(ADMIN_ID[0], "Processed successfully!")
                process = 1
            output = request.get_json()
            for event in output['entry']:
                if event.get('messaging'):
                    messaging = event['messaging']
                    for message in messaging:
                        if message.get('message'):
                            recipient_id = message['sender']['id']
                            if recipient_id == PAGE_ID:
                                continue
                            mark_seen(recipient_id)
                            if (users.is_banned(recipient_id)):
                                send_text(recipient_id, saves['account banned'])
                                continue
                            if matching.get(recipient_id):
                                matching.update(recipient_id)
                            if maintenance == 1 and not recipient_id in ADMIN_ID:
                                send_text(recipient_id, saves['maintenance'])
                                continue
                            if message['message'].get('quick_reply'):
                                users.quickrep(recipient_id, message['message']['quick_reply']['payload'])
                                continue
                            if message['message'].get('attachments'):
                                response = send_message_attachment(recipient_id, message['message'])
                                if response == 'error':
                                    send_text(recipient_id, saves['attachment failed'])
                            elif message['message'].get('text'):
                                if message['message'].get('reply_to'):
                                    send_text(recipient_id, saves['react'])
                                    continue
                                response = send_message_text(recipient_id, message['message'])
                                if response == 'error':
                                    send_text(recipient_id, saves['unexpected error'])
                        elif message.get('postback'):
                            recipient_id = message['sender']['id']
                            if recipient_id == PAGE_ID:
                                continue
                            mark_seen(recipient_id)
                            if (users.is_banned(recipient_id)):
                                send_text(recipient_id, saves['account banned'])
                                continue
                            if maintenance == 1:
                                send_text(recipient_id, saves['maintenance'])
                                continue
                            users.postback(recipient_id, message['postback'])

        except Exception:
            errnum = traceback.format_exc()
            cur = datetime.now()
            cur = cur.strftime("%m/%d/%Y, %H:%M:%S")
            f = open("log.txt", 'a+', encoding='utf-8')
            f.write(cur + '\n')
            f.write(errnum + '\n\n\n')
            f.close()

    return "ok"

@app.route("/docs", methods = ['GET'])
def docs():
    return render_template('docs.html')

@app.route("/changelog", methods=['GET'])
def changelog():
    return render_template('changelog.html')

#verify this change
def verify_token(token):
	if token == VERIFY_TOKEN:
		return request.args.get("hub.challenge")
	return '404 Not found'

#all commands
def command(recipient_id, text):
    global maintenance
    global process
    global free_premium
    if len(text) == 0 or text[0] != '/':
        return 0
    text = [i for i in text.split()]
    if text[0] == '/end':
        users.end(recipient_id)
    elif text[0] == '/start':
        users.get_started(recipient_id,forces=1)
    elif text[0] == '/help':
        users.help(recipient_id)
    elif text[0] == '/report':
        users.report(recipient_id, text)
    elif text[0] == '/keep':
        users.keep(recipient_id)
    elif text[0] == '/rc':
        users.prom8(recipient_id, text)
    elif text[0] == '/plan':
        expiry = users.is_premium(recipient_id)
        if expiry:
            expiry = expiry.strftime("%H:%M:%S %d/%m/%Y")
            send_text(recipient_id, saves['donator'] + expiry)
        else:
            send_text(recipient_id, saves['premium require'])
    elif text[0] == '/music':
        if recipient_id in ADMIN_ID or users.is_premium(recipient_id) or free_premium:
            users.search_music(recipient_id, text)
        else:
            send_text(recipient_id, saves['premium require'])
        return 0
    elif text[0] == '/kill' and recipient_id in ADMIN_ID:
        try:
            matching.kill(text[1], text[2])
        except:
            send_text(recipient_id, "Cannot execute request")
    elif text[0] == '/shutdown' and recipient_id in ADMIN_ID:
        maintenance = 1
        send_text(recipient_id, saves['command executed'])
    elif text[0] == '/turnon' and recipient_id in ADMIN_ID:
        maintenance = 0
        send_text(recipient_id, saves['command executed'])
    elif text[0] == '/inform' and recipient_id in ADMIN_ID:
        if len(text) < 2:
            send_text(recipient_id, saves['wrong syntax'])
        else:
            users.inform(text)
    elif text[0] == '/execute' and recipient_id == ADMIN_ID[0]:
        if (process):
            send_text(recipient_id, "Already processed")
        else:
            send_text(recipient_id, "Processing!")
            worker = multiprocessing.Process(target=ultility.run)
            worker.start()
            worker1 = multiprocessing.Process(target=matching.autoend)
            worker1.start()
            send_text(recipient_id, "Processed successfully!")
            process = 1
    elif text[0] == '/database' and recipient_id in ADMIN_ID:
        users.database(recipient_id, text)
    elif text[0] == '/ban' and recipient_id in ADMIN_ID:
        users.ban(recipient_id, text)
    elif text[0] == '/unban' and recipient_id in ADMIN_ID:
        users.unban(recipient_id, text)
    elif text[0] == '/premium' and recipient_id in ADMIN_ID:
        users.premium(recipient_id, text)
    elif text[0] == '/unpremium' and recipient_id in ADMIN_ID:
        users.unpremium(recipient_id, text)
    elif text[0] == '/token' and recipient_id in ADMIN_ID:
        users.token(recipient_id, text)
    else:
        send_text(recipient_id, saves['no command'])
    return 1

#receive message with texts
def send_message_text(recipient_id, message):
    message.pop('mid', None)
    if command(recipient_id, message['text']):
        return
    if matching.get(recipient_id) == '':
        users.get_started(recipient_id)
        return
    isPremium = (recipient_id in ADMIN_ID or users.is_premium(recipient_id) or free_premium)
    recipient_id = matching.get(recipient_id)
    data = {
        "message": message,
        "recipient" : {
            "id" : recipient_id
        },
        "message_type" : "MESSAGE_TAG",
        "tag" : "ACCOUNT_UPDATE"
    }
    if isPremium:
        data['persona_id'] = "1017320656484965"
    return send_message(data)

#recieve message with attachments
def send_message_attachment(recipient_id, message):
    if matching.get(recipient_id) == "":
        users.get_started(recipient_id)
        return
    old_id = recipient_id
    recipient_id = matching.get(recipient_id)
    if int(old_id) == 6433851309962620 or int(recipient_id) == 6433851309962620:
        return
    message.pop('mid', None)
    data = {
        "recipient" : {
            "id" : recipient_id
        },
        "message" : {
            "attachment" : {
                "type" : "",
                "payload" : ""
            }
        }
    }
    response = 'success'
    for attachment in message['attachments']:
        if attachment['type'] == 'fallback':
            messagess = {
                "text" : message['text']
            }
            if send_message_text(old_id, messagess) == 'error':
                response = 'error'
            continue
        elif not attachment['type'] in ATTACHMENTS:
            continue
        if attachment['type'] == 'video':
            send_text(old_id, "Bạn không thể gửi video ở chế độ này. Việc gửi nội dung có dung lượng quá lớn sẽ khiến page quá tải")
            continue
        if attachment['type'] == 'image' and users.is_premium(recipient_id) and valid.check_image(attachment['payload']['url']):
            a = []
            b = []
            for admin in ADMIN_ID:
                a.append(admin)
                b.append(str(recipient_id) + " violate image rules")
            a.append(old_id)
            b.append("Ảnh của bạn đã vi phạm quy tắc. Hãy lưu ý rằng các hành động lặp lại tương tự có thể khiến bạn bị cấm sử dụng")
            send_texts(a, b)
            continue
        data['message']['attachment']['type'] = attachment['type']
        attachment['payload'].pop('sticker_id', None)
        data['message']['attachment']['payload'] = attachment['payload']
        if send_message(data) == 'error':
            response = 'error'
    return response

#messenger api POST request
def send_message(data):
    if data.get('recipient') and int(data['recipient']['id']) == int(PAGE_ID):
        return
    content = requests.post(message_url, json = data)
    if 'error' in content.text:
        f = open(LOG, 'a+', encoding='utf-8')
        cur = datetime.now()
        f.write(cur.strftime("%m/%d/%Y, %H:%M:%S") + "\n")
        f.write(content.text + '\n')
        f.write('reason: \n')
        f.write(str(data) + '\n\n')
        f.close()
        return 'error'
    return 'success'


def send_messages(list):
    ret = []
    async def send_multitext(list):
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = []
            for data in list:
                tasks.append(asyncio.create_task(session.post(message_url, json=data, ssl=False)))
            responses = await asyncio.gather(*tasks)
            for response in responses:
                ret.append(await response.json())
        return ret
    return asyncio.run(send_multitext(list))

#only for text
def send_text(recipient_id, text):
    data = {
        "message" : {
            "text" : text
        },
        "recipient" : {
            "id" : recipient_id
        },
        "message_type" : "MESSAGE_TAG",
        "tag" : "ACCOUNT_UPDATE"
    }
    send_message(data)

def send_texts(recipient_id, text):
    ret = []
    async def send_multitext(recipient_ids, texts):
        if len(recipient_ids) != len(texts):
            return "Failed"
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = []
            for i in range(0, len(recipient_ids)):
                data = {
                    "message" : {
                        "text" : texts[i]
                    },
                    "recipient" : {
                        "id" : recipient_ids[i]
                    },
                    "message_type" : "MESSAGE_TAG",
                    "tag" : "ACCOUNT_UPDATE",
                }
                tasks.append(asyncio.create_task(session.post(message_url, json=data, ssl=False)))
            responses = await asyncio.gather(*tasks)
            for response in responses:
                ret.append(await response.json())
        return ret
    return asyncio.run(send_multitext(recipient_id, text))


def mark_seen(recipient_id):
    data = {
        "recipient" : {
            "id" : recipient_id
        },
        "sender_action" : "mark_seen"
    }
    send_message(data)

if __name__ == "__main__":
    app.run(debug=1,port=80)