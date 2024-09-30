import requests, os, time
import config, json, ultility, pytube
import multiprocessing, matching
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urlencode
import asyncio, aiohttp

PAGE_ACCESS_TOKEN = config.PAGE_ACCESS_TOKEN
message_url = f"https://graph.facebook.com/v15.0/{config.PAGE_ID}/messages?access_token={PAGE_ACCESS_TOKEN}"
conversation_url = f"https://graph.facebook.com/v15.0/me/conversations?fields=participants&access_token={PAGE_ACCESS_TOKEN}"
download_url = f"http://srv11.onlymp3.to/download?file=5cfa0d7f723450e21f5a23a39fcf1cb8140003&token=8w4SkeW1j0uCS7WFCAgMmA&expires=1657665717877&s=-aJxdYbTViw0CJ-KWj6ojw?"



url = f'https://graph.facebook.com/v2.10/me/message_attachments?access_token={PAGE_ACCESS_TOKEN}'

data = {
    'type' : 1,
    'message' : 'https://youtube.com/watch?v=MSRcC626prw'
}

import tts
tts.tts(1, "Mẹ mày béo")