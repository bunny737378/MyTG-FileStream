import os

def handler(request, response):
    os.system("python3 -m tgfs")
    return response.send("tgfs module executed (once)")
