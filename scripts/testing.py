import subprocess
import json

url = "http://localhost:8000/accounts"

def next_name(value):
    chrs = list(value)
    i = len(chrs)-1
    while i >= 0:
        if chrs[i] != 'Z':
            chrs[i] = chr(ord(chrs[i])+1)
            break
        chrs[i] = 'A'
        i -= 1

    return "".join(chrs)

def get_name(value):
    while True:
        yield value
        value = next_name(value)

generator = get_name("ABCD")

for i in range(100):
    name = next(generator)
    params = json.dumps({"owner_name": name, "currency": "INR"})
    result = subprocess.run(["curl", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", params])