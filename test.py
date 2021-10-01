import requests
import sys

cmd = input('Command: ')
session = sys.argv[1] or ''

if cmd == 'new':
    r = requests.get('http://localhost:6666/new')
    print(r.json())
elif cmd == 'cmd':
    r = requests.post('http://localhost:6666/cmd', data={
            'session': session,
            'cmd': input("cmd: ")
        })
    print(r.json())
elif cmd == 'result':
    r = requests.post('http://localhost:6666/result', data={
            'session': session,
            'id': input("id: ")
        })
    print(r.json())
else:
    print("new, cmd, result")
