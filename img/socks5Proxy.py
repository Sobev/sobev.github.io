import socket
import threading
import select



SOCKS_VERSION = 5

#https://github.com/shikanon/socks5proxy/wiki 中文SOCKS5参考地址

class Proxy:
    def __init__(self):
        self.username = "username"
        self.password = "password"

    def handle_client(self, connection):
        # greeting header
        # read and unpack 2 bytes from a client
        # VER是SOCKS版本，这里应该是0x05；
        # NMETHODS是METHODS部分的长度；

        version, nmethods = connection.recv(2)
        print("version: {}, nmethods: {}".format(version, nmethods))
        # get available methods [0, 1, 2]
        # METHODS是客户端支持的认证方式列表，每个方法占1字节。当前的定义是：
        # 0x00 不需要认证
        # 0x01 GSSAPI
        # 0x02 用户名、密码认证
        # 0x03 - 0x7F由IANA分配（保留）
        # 0x80 - 0xFE为私人方法保留
        # 0xFF 无可接受的方法
        methods = self.get_available_methods(nmethods, connection)
        print("available methods: {}".format(methods))
        # accept only USERNAME/PASSWORD auth
        if 2 not in set(methods):
            # close connection
            print("2 not in method")
            connection.close()
            return

        # send welcome message
        connection.sendall(bytes([SOCKS_VERSION, 2]))

        if not self.verify_credentials(connection):
            return

        # request (version=5)
        version, cmd, _, address_type = connection.recv(4)
        print("version: {}, cmd: {}, address_type; {}".format(version, cmd, address_type))

        if address_type == 1:  # IPv4
            address = socket.inet_ntoa(connection.recv(4))
        elif address_type == 3:  # Domain name
            domain_length = connection.recv(1)[0]
            address = connection.recv(domain_length)
            address = socket.gethostbyname(address)

        # convert bytes to unsigned short array
        port = int.from_bytes(connection.recv(2), 'big', signed=False)

        try:
            if cmd == 1:  # CONNECT
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((address, port))
                bind_address = remote.getsockname()
                print("* Connected to {} {}".format(address, port))
            else:
                connection.close()

            addr = int.from_bytes(socket.inet_aton(bind_address[0]), 'big', signed=False)
            port = bind_address[1]

            reply = b''.join([
                SOCKS_VERSION.to_bytes(1, 'big'),
                int(0).to_bytes(1, 'big'),
                int(0).to_bytes(1, 'big'),
                int(1).to_bytes(1, 'big'),
                addr.to_bytes(4, 'big'),
                port.to_bytes(2, 'big')
            ])
        except Exception as e:
            # return connection refused error
            reply = self.generate_failed_reply(address_type, 5)

        connection.sendall(reply)

        # establish data exchange
        if reply[1] == 0 and cmd == 1:
            self.exchange_loop(connection, remote)

        connection.close()

    
    def exchange_loop(self, client, remote):
        # select()方法接收并监控3个通信列表
        # 第一个是所有的输入的data,就是指外部发过来的数据，
        # 第2个是监控和接收所有要发出去的data(outgoing data)
        # 第3个监控错误信息
        while True:
            # wait until client or remote is available for read
            r, w, e = select.select([client, remote], [], [])

            if client in r:
                data = client.recv(4096)
                if remote.send(data) <= 0:
                    break

            if remote in r:
                data = remote.recv(4096)
                if client.send(data) <= 0:
                    break

    
    def generate_failed_reply(self, address_type, error_number):
        return b''.join([
            SOCKS_VERSION.to_bytes(1, 'big'),
            error_number.to_bytes(1, 'big'),
            int(0).to_bytes(1, 'big'),
            address_type.to_bytes(1, 'big'),
            int(0).to_bytes(4, 'big'),
            int(0).to_bytes(4, 'big')
        ])


    def verify_credentials(self, connection):
        version = ord(connection.recv(1)) # should be 1

        username_len = ord(connection.recv(1))
        print("username_len: {}".format(username_len))
        username = connection.recv(username_len).decode('utf-8')
        print("username: {}".format(username))

        password_len = ord(connection.recv(1))
        print("password_len: {}".format(password_len))
        password = connection.recv(password_len).decode('utf-8')
        print("password: {}".format(password))

        if username == self.username and password == self.password:
            # success, status = 0
            response = bytes([version, 0])
            connection.sendall(response)
            return True

        # failure, status != 0
        response = bytes([version, 0xFF])
        connection.sendall(response)
        connection.close()
        return False


    def get_available_methods(self, nmethods, connection):
        methods = []
        for i in range(nmethods):
            methods.append(ord(connection.recv(1)))
        return methods

    def run(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()

        print("* Socks5 proxy server is running on {}:{}".format(host, port))

        while True:
            conn, addr = s.accept()
            print("* new connection from {}".format(addr))
            t = threading.Thread(target=self.handle_client, args=(conn,))
            t.start()


if __name__ == "__main__":
    proxy = Proxy()
    proxy.run("127.0.0.1", 18300)