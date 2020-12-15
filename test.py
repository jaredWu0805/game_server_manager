import socket

for host in [ 'homer', 'github.com', 'www.engadget.com', 'DESKTOP-8IMDH48']:
# for host in ['172.16.0.147', '216.58.200.46']:
    try:
        print('%15s : %s' % (host, socket.gethostbyaddr(host)))
        print(  '- %s' % (socket.getfqdn(host)))
    except socket.error as msg:
        print('%15s : ERROR: %s' % (host, msg))