import json

import threading
import time
import redis
import requests


class proxypool(object):
    _instance_lock = threading.Lock()

    def __init__(self, server, iport, password=None):
        if password:
            self.redis_pool = redis.ConnectionPool(host=server, port=iport, password=password, decode_responses=True)
        else:
            self.redis_pool = redis.ConnectionPool(host=server, port=iport, decode_responses=True)

    def __new__(cls, *args, **kwargs):
        if not hasattr(proxypool, "_instance"):
            with proxypool._instance_lock:
                if not hasattr(proxypool, "_instance"):
                    proxypool._instance = object.__new__(cls)
        return proxypool._instance

    def __del__(self):
        if self.redis_pool is not None:
            self.redis_pool.disconnect()
            self.redis_pool = None
            print("proxy pool del.")

    def get_proxy(self):
        '''
        返回redis 代理池资源，每次返回一个长度为35的list
        :param timeout: 
        :return: 
        '''
        try:
            r = redis.StrictRedis(connection_pool=self.redis_pool)
            proxies_list = r.keys()
            return proxies_list
        except Exception as e:
            # logger.error("get_proxy exception:"+e.__str__())
            print("error : " + e.__str__())
        return ""

    def close(self):
        self.redis_pool.disconnect()
