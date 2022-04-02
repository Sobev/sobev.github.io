import socket
import sys
from _thread import *

def main():
    global liten_port, buffer_size, max_conn
    try:
        listen_port = int(input("Enter the port number to listen on: "))
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    max_conn = 5
    buffer_size = 8192

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', listen_port))
        s.listen(max_conn)
        print("[*] Initializing socket Done...")
        print("[*] Socket bind Successfully...")
        print("[*] Server started Successfully [{}]".format(listen_port))
    except Exception as e:
        print("[0] Error: {}".format(e))
        sys.exit(2)
    while True:
        try:
            conn, addr = s.accept()
            data = conn.recv(buffer_size)
            start_new_thread(conn_string, (conn, data, addr))
        except KeyboardInterrupt:
            s.close()
            print("\Shuting Down...")
            sys.exit(1)
    s.close()


def conn_string(conn, data, addr):
    try:
        first_line = data.decode("utf-8").split('\n')[0]
        url = first_line.split(' ')[1]

        http_pos = url.find("://")
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]

        port_pos = temp.find(":")
        
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        
        web_server = ""
        port = -1

        if port_pos == -1 or webserver_pos < port_pos:
            port = 80
            web_server = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            web_server = temp[:port_pos]

        proxy_server(web_server, port, conn, data, addr)
    except Exception as e:
        print("[1] Error: {}".format(e))
        sys.exit(2)


def proxy_server(web_server, port, conn, data, addr):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((web_server, port))
        # print(data.decode("utf-8"))
        s.send(data)
        print("[*] Request sent to {}:{}".format(web_server, port))
        while True:
            reply = s.recv(buffer_size)
            if len(reply) > 0:
                conn.send(reply)
                dar = float(len(reply))
                dar = dar/1024
                dar = "{}".format(dar)
                print("[*] Request Done {} => {} <= {}".format(addr[0], dar, web_server))
                print(reply.decode("utf-8"))
            else:
                break
        s.close()
        conn.close()
    except Exception as e:
        conn.close()
        s.close()
        print("[2] Error: {}".format(e))
        sys.exit(2)

if __name__ == "__main__":
    main()