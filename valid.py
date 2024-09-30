import requests
import json, app
import config

params = {
  'url': 'https://sightengine.com/assets/img/examples/example7.jpg',
  'models': 'nudity-2.0,gore',
  'api_user': config.SIGHTENGINE_API_USER,
  'api_secret': config.SIGHTENGINE_API_SECRET
}

def check_image(url):
    try:
        params['url'] = url
        response = requests.get('https://api.sightengine.com/1.0/check.json', params=params)
        response = json.loads(response.text)
        return float(response['nudity']['none']) < 0.2 or float(response['gore']['prob']) > 0.1
    except:
        for admin in config.ADMIN_ID:
            app.send_text(admin, "Out of 2000 checks")
        return 1