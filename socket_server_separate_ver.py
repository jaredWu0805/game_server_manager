import socket
import sys
from requests import get, post

HOST = '0.0.0.0'
RCV_PORT = 5566
SD_PORT = 5567
http_url = 'http://192.168.10.116:5000'
# http_url = 'http://172.16.0.147:5000'

s_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_recv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s_recv.bind((HOST, RCV_PORT))
s_recv.listen(5)

s_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s_send.bind((HOST, SD_PORT))
s_send.listen(5)

print('receiving server start at: {0} {1}'.format(HOST, RCV_PORT))
print('wait for connection...')


while True:
    conn, addr = s_recv.accept()
    # s_conn, addr_s = s_send.accept()
    print('connected to: ' + str(addr))
    print('Open another sending socket port: ' + str(s_send.getsockname()))

    while True:
        input_data = conn.recv(1024)
        # connection closed
        if len(input_data) == 0 or input_data.decode() == 'exit':
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            # s_conn.close()
            print('client closed connection.')
            break

        data = input_data.decode()
        print('recv: ' + data)

        # if data == 'games':
            # game_server_data = get('{0}/games'.format(http_url)).json()
            # data = game_server_data['ip']
            # print(data)

        # if data == 'Open game':
        game_server_data = get('{0}/games/1/play'.format(http_url)).json()
        ip = game_server_data['game server ip']
        print(ip)

        output_data = 'echo: ' + data + ' ip: ' + ip
        print(output_data)
        # s_send.send(output_data.encode())
        conn.send(output_data.encode())

