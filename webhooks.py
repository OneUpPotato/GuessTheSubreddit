from json import dumps
from requests import post

import settings

def post_submissions_webhook(data):
    try:
        data = dumps({"embeds":[data]})
        request = post(settings.get_submissions_webhook(), data=data, headers={"Content-Type":"application/json"})
        if request.status_code in [200, 204]:
            print("Succesfully messaged using webhook.")
        else:
            print(request.status_code, request.text)
            print("Problem messaging using webhook.")
    except:
        pass
