import socket
import select
import threading
import datetime
import time
from array import *


connected_socket = []

def coroutine_one():
    host = ['202.129.173.59', '202.129.173.60']
    port = [8040, 8040]
    ais_key_str = ['014e4d45415f4d444d004e4d45415f4d444d00', '014e4d45415f4d444d004e4d45415f4d444d00']

    timeout = 30
    targetHost = 0   

    while True:

        aiskey = array('b', [])
        keyLenCnt = 0
        keyHexVal = ''
        
        for n in range(int(len(ais_key_str[targetHost]))):
            keyHexVal += ais_key_str[targetHost][n:n+1]
            keyLenCnt += 1

            if keyLenCnt % 2 == 0:
                aiskey.append(int(keyHexVal, 16))
                keyHexVal = ''



        try:
            data = ''
            defaultTime = datetime.datetime(1900, 1, 1, 00, 00, 00)
            now = datetime.datetime(1900, 1, 1, 00, 00, 00)

            print(f'attempt to server {host[targetHost]} via port {port[targetHost]}...')

            sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sc.connect((host[targetHost], port[targetHost]))
            sc.settimeout(timeout)
            sc.setblocking(0)        #set to unblocking socket operation
            sc.send(aiskey)

            print('connected...')
            targetHost += 1
            targetHost = 0 if targetHost > len(host) else targetHost


            while True:
                try:       
                    recvData = sc.recv(1)
                    now = defaultTime

                    if len(recvData) == 0:
                        raise Exception

                    data += recvData.decode()

                    if recvData.decode() == '\n':
                        if data.strip()[0:1] == '!':
                            ais_sentence = data.strip()
                            print(ais_sentence)

                            if len(connected_socket)>0 :
                                for i in connected_socket:
                                    i.send(ais_sentence.encode('utf-8'))
                                    


                        data = ''

                    if sc.fileno() == -1:
                        break
                except:
                    if now == defaultTime:
                        now = datetime.datetime.now()

                    dt = datetime.datetime.now() - now
                    
                    if dt.total_seconds() > timeout:
                        break

                    continue
            
            sc.close()
            sc.detach()
            print('timeout - process exited!')

            time.sleep(1)
        except:
            sc.detach()

            print('network reconnection....')
            time.sleep(3)

            targetHost += 1
            targetHost = 0 if targetHost >= len(host) else targetHost

            continue



def main():
    # Create a socket object
    s = socket.socket()

    # Get local machine name
    host = socket.gethostname()

    # Reserve a port for your service
    port = 38383

    # Bind to the port
    s.bind((host, port))

    # Set the socket to non-blocking mode
    s.setblocking(0)

    # Wait for client connection
    s.listen(5)

    # List of sockets to be monitored by select
    sockets_to_monitor = [s]


    thread_one = threading.Thread(target=coroutine_one)
    thread_one.start()

    while True:
        # try:
        #     c, addr = s.accept()
        #     print('Got connection from', addr)

        #     c.send(b'hello')
        # except:        
        #     er = 'error'

        # # Use select to get the list of sockets ready for reading
        readable, _, _ = select.select(sockets_to_monitor, [], [])

        for sock in readable:
            
            if sock is s:
                # A new client connection is ready to be accepted
                c, addr = s.accept()
                print('Got connection from', addr)
                sockets_to_monitor.append(c)
                connected_socket.append(c)
            else:
                try:
                    # An existing client sent data or closed the connection
                    data = sock.recv(256)
                    print("data::" + data.decode("utf-8"))

                    if data:
                        sock.send(data)

                    else:
                        sock.close()
                        sockets_to_monitor.remove(sock)
                        connected_socket.remove(sock)
                except:
                        sock.close()
                        sockets_to_monitor.remove(sock)
                        connected_socket.remove(sock)                    



if __name__ == '__main__':
    main()