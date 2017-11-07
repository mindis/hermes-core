# coding: utf-8
import socket
import base64
import queue
import threading
from unittest import TestCase, main

import pyhermes


class TCPTransport:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def __del__(self):
        if self.socket:
            self.socket.close()

    def send(self, msg):
        total_sent = 0
        while total_sent < len(msg):
            sent = self.socket.send(msg[total_sent:])
            if not sent:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    def receive(self, needed_length):
        data = self.socket.recv(needed_length)
        if not data:
            raise RuntimeError("socket connection broken")
        return data


class BufferTransport:
    def __init__(self, buffer_in: queue.Queue, buffer_out: queue.Queue):
        self.buffer_in = buffer_in
        self.buffer_out = buffer_out

    def send(self, msg):
        self.buffer_out.put(msg)

    def receive(self, needed_length):
        data = self.buffer_in.get()
        if not data or len(data) != needed_length:
            raise RuntimeError("socket connection broken")
        self.buffer_in.task_done()
        return data


class TestHermesTransport(TestCase):
    TIMEOUT = 1

    USER_ID1 = b'user1'
    PRIVATE_KEY1 = base64.b64decode(b'UkVDMgAAAC0Tj5tGAPfpgfYMBACxX6onvlWvcc2Gb9ZylBlJdjebTpV3OCIx')
    PUBLIC_KEY1 = base64.b64decode(b'VUVDMgAAAC2ISqIZApjrN6BCVmWoJdbhjN2EmBAfLq3VKEdRnz0gVdYcIDQp')

    USER_ID2 = b'user2'
    PRIVATE_KEY2 = base64.b64decode(b'UkVDMgAAAC00lzw7ABmvKHvjOqWW8i+dxwHTU8RzuaATkZNBcLmCm8TBxRn2')
    PUBLIC_KEY2 = base64.b64decode(b'VUVDMgAAAC0lAFeZAqw+nKzco1l2qtXELqVr7fmpsMf4hSrOa/TkAu5OQ6Cy')

    def create_transport(self, user_id, private, public_id, public, transport, is_server, result):
        def f():
            hermes_transport = pyhermes.SecureHermesTransport(user_id, private, public_id, public, transport, is_server)
            if is_server:
                result.put(hermes_transport, True)
            else:
                result.put(hermes_transport, False)
        return f

    def test_transport(self):
        buffer_in = queue.Queue()
        buffer_out = queue.Queue()
        result = queue.Queue()
        transportClient = BufferTransport(buffer_out, buffer_in)
        transportServer = BufferTransport(buffer_in, buffer_out)

        server_thread = threading.Thread(target=self.create_transport(self.USER_ID1, self.PRIVATE_KEY1, self.USER_ID2, self.PUBLIC_KEY2, transportServer, True, result))
        server_thread.start()
        client_thread = threading.Thread(target=self.create_transport(self.USER_ID2, self.PRIVATE_KEY2, self.USER_ID1, self.PUBLIC_KEY1, transportClient, False, result))
        client_thread.start()

        server_thread.join(timeout=self.TIMEOUT)
        client_thread.join(timeout=self.TIMEOUT)
        buffer_in.join()
        buffer_out.join()

        # wait result from threads
        transportA, transportB = [result.get(timeout=self.TIMEOUT) for _ in range(2)]


class TestHermes(TestCase):
    USER_ID1 = b'user1'
    PRIVATE_KEY1 = base64.b64decode(b'UkVDMgAAAC0Tj5tGAPfpgfYMBACxX6onvlWvcc2Gb9ZylBlJdjebTpV3OCIx')
    PUBLIC_KEY1 = base64.b64decode(b'VUVDMgAAAC2ISqIZApjrN6BCVmWoJdbhjN2EmBAfLq3VKEdRnz0gVdYcIDQp')

    USER_ID2 = b'user2'
    PRIVATE_KEY2 = base64.b64decode(b'UkVDMgAAAC00lzw7ABmvKHvjOqWW8i+dxwHTU8RzuaATkZNBcLmCm8TBxRn2')
    PUBLIC_KEY2 = base64.b64decode(b'VUVDMgAAAC0lAFeZAqw+nKzco1l2qtXELqVr7fmpsMf4hSrOa/TkAu5OQ6Cy')

    CREDENTIAL_ID = b"credential_store"
    #CREDENTIAL_PRIVATE = base64.b64decode(b"UkVDMgAAAC1P6i5PAMI1t4G2xrmsMKi4TDVZ6ut6NsAOltsVcGga6qjEZBLp")
    CREDENTIAL_PUBLIC = base64.b64decode(b"VUVDMgAAAC1x1lf9Az0bNDSYU8TG8XcBBwsciK6nOo4H9/VeSb2carumNQla")

    KEY_STORE_ID = b"key_store_server"
    #KEY_STORE_PRIVATE = base64.b64decode(b"UkVDMgAAAC1Mgh02ALY2AAa2J6peDmvEOQSN6+M8m6s/ZqTp0ffiZGcHsTgY")
    KEY_STORE_PUBLIC = base64.b64decode(b"VUVDMgAAAC3QMLOAAoms9u5nTh1Ir3AnTPt5RkMJY9leIfF6uMIxms/Bkywp")

    DATA_STORE_ID = b"data_store_server"
    #DATA_STORE_PRIVATE = base64.b64decode(b"UkVDMgAAAC0tLpmOAEJCDkGPTr+l2jo+LWUbB7uSX567nzgmMfODl4wWTAH4")
    DATA_STORE_PUBLIC = base64.b64decode(b"VUVDMgAAAC0VCQ/fAt88d2N8vDFVAKbDJHsXew8HgB55PIrVfhELXrEf1N89")

    def test_full(self):
        try:
            credential_store_transport1 = pyhermes.SecureHermesTransport(
                self.USER_ID1, self.PRIVATE_KEY1, self.CREDENTIAL_ID, self.CREDENTIAL_PUBLIC,
                TCPTransport("127.0.0.1", 8888), False)
            key_store_transport1 = pyhermes.SecureHermesTransport(
                self.USER_ID1, self.PRIVATE_KEY1, self.KEY_STORE_ID, self.KEY_STORE_PUBLIC,
                TCPTransport("127.0.0.1", 8889), False)
            data_store_transport1 = pyhermes.SecureHermesTransport(
                self.USER_ID1, self.PRIVATE_KEY1, self.DATA_STORE_ID, self.DATA_STORE_PUBLIC,
                TCPTransport("127.0.0.1", 8890), False)

            credential_store_transport2 = pyhermes.SecureHermesTransport(
                self.USER_ID1, self.PRIVATE_KEY1, self.CREDENTIAL_ID, self.CREDENTIAL_PUBLIC,
                TCPTransport("127.0.0.1", 8888), False)
            key_store_transport2 = pyhermes.SecureHermesTransport(
                self.USER_ID1, self.PRIVATE_KEY1, self.KEY_STORE_ID, self.KEY_STORE_PUBLIC,
                TCPTransport("127.0.0.1", 8889), False)
            data_store_transport2 = pyhermes.SecureHermesTransport(
                self.USER_ID1, self.PRIVATE_KEY1, self.DATA_STORE_ID, self.DATA_STORE_PUBLIC,
                TCPTransport("127.0.0.1", 8890), False)
        except ConnectionRefusedError:
            self.skipTest("credential|key|data store service not started on 8888|8889|8890 port respectively")

        mid_hermes1 = pyhermes.MidHermes(
            self.USER_ID1, self.PRIVATE_KEY1,
            credential_store_transport1, data_store_transport1,
            key_store_transport1)

        mid_hermes2 = pyhermes.MidHermes(
            self.USER_ID2, self.PRIVATE_KEY2,
            credential_store_transport2, data_store_transport2,
            key_store_transport2)

        block_id = b'test id'
        block_data = b'test data'
        block_meta = b'meta 1'

        mid_hermes1.addBlock(block_id, block_data, block_meta)
        self.assertEqual(mid_hermes1.getBlock(block_id), (block_data, block_meta))

        new_data = b'new data'

        mid_hermes1.updBlock(block_id, new_data, block_meta)

        self.assertEqual(mid_hermes1.getBlock(block_id), (new_data, block_meta))

        mid_hermes1.grantReadAccess(block_id, self.USER_ID2)
        self.assertEqual(mid_hermes2.getBlock(block_id), (new_data, block_meta))

        mid_hermes1.grantUpdateAccess(block_id, self.USER_ID2)

        new_data2 = b'new data 2'
        mid_hermes2.updBlock(block_id, new_data2, block_meta)

        self.assertEqual(mid_hermes1.getBlock(block_id), (new_data2, block_meta))
        self.assertEqual(mid_hermes2.getBlock(block_id), (new_data2, block_meta))

        mid_hermes1.denyUpdateAccess(block_id, self.USER_ID2)
        try:
            mid_hermes2.updBlock(block_id, new_data, block_meta)
        except:
            pass

        mid_hermes1.denyReadAccess(block_id, self.USER_ID2)
        try:
            mid_hermes2.getBlock(block_id)
        except:
            pass

        mid_hermes1.delBlock(block_id)

if __name__ == '__main__':
    main()