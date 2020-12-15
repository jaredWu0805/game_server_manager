import socket
import sys
from requests import get, post

HOST = '0.0.0.0'
PORT = 5566
BUFFER_SIZE = 1024
game_server_url = 'localhost:5000'


def portal_socket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        print('Listening on {0}:{1}'.format(HOST, PORT))

        while True:
            print('waiting for connection...')
            conn, addr = s.accept()
            print('connected to: ' + str(addr))
            while True:
                input_data = conn.recv(BUFFER_SIZE)

                # connection closed
                if len(input_data) == 0 or input_data.decode() == 'exit':
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                    print('client closed connection.')
                    break

                try:
                    data = input_data.decode()
                    print('recv: \n' + data)
                    req = data.split(',')

                    if req[0] == "get":
                        data = socket_get(req[1:])
                    elif req[0] == "launch":
                        data = socket_launch(req[1:], addr[0])
                    elif req[0] == "close":
                        pass

                    print('echo: \n' + data)
                    conn.send(data.encode())
                except Exception as e:
                    print(e)
                    print("connection abort...")
                    conn.close()

            # sys.exit()


def socket_get(arg: list):
    try:
        src_type = arg[0]
        print(src_type)
        req_url = 'http://{0}/{1}'.format(game_server_url, src_type)
        if len(arg) == 2:
            req_url += arg[1]
        print(req_url)
        game_server_data = get(req_url).json()
        print(game_server_data)
        if not game_server_data['status']:
            return "No such game"
        else:
            return "IP," + game_server_data['ip']
    except Exception as e:
        print(e)
        return "Server error"


def socket_launch(arg: list, addr):
    try:
        src_type = arg[0]
        # item_id = arg[1]
        print('http://{0}/{1}/1/launch?client_ip={2}'.format(game_server_url, src_type, addr))
        game_server_data = get('http://{0}/{1}/1/launch?client_ip={2}'.format(game_server_url, src_type, addr)).json()
        print(game_server_data)
        if not game_server_data['game server ready']:
            return game_server_data['msg']
        else:
            return "IP," + game_server_data['game server ip']

    except Exception as e:
        print(e)
        return "Server error"


portal_socket()
