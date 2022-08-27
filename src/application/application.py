from eqsmart.components.scan_services import ScanServices
from eqsmart.components.read_module import ReadModule
from eqsmart.main.http_servr import http_server
from eqlink.main.clent import LinkClient, time_sleep, fail_server_list
from threading import Thread
import traceback
from sys import path as sys_path

sys_path.append('../..')

try:
    from src.application.configuration.conf_all import AllConf
except Exception as e:
    print(e, traceback.format_exc())
    exit(0)
'''加载配置文件'''
app_conf_profile = 'configuration/profiles/app.yaml'
AC = AllConf(app_conf_profile)

'''组件加载器'''
read_conf_module = ReadModule('configuration')


class Register:
    def __init__(self, path):
        """
        注册中心连接工具初始化
        :param path: 配置文件路径
        """
        ''' 注册中心的配置信息 '''
        self.link_conf = read_conf_module.read('conf_center').LinkServerConf(path).read_server()
        ''' 服务消费者配置信息 '''
        self.consumer_conf = read_conf_module.read('conf_consumer').ConsumerServerConf(path).read_server()

    def keep_connect(self):
        """
        Consumer 与注册中心的连接器
        :return: 连接器
        """
        return LinkClient(self.link_conf, self.consumer_conf)


class Application:
    def __init__(self, path):
        """
        app初始化
        :param path: 配置文件路径
        """
        self.conf_path = path
        ''' HTTP服务列表扫描 '''
        scan_http_services = ScanServices('../gateway')
        self.http_services = scan_http_services.get_services()
        self.http_services_class = scan_http_services.get_services_class()
        self.http_conf = read_conf_module.read('conf_http').HttpServerConf(path).read_server()

    def __connect_link__(self):
        """ Consumer 启动并保持与注册中心的连接 """
        ''' 实例化一个消费者注册器 '''
        consumer_register = Register(self.conf_path)
        ''' Consumer到注册中心的连接器 '''
        consumer_connect = consumer_register.keep_connect()
        ''' Consumer与注册中心断线重连的配置 '''
        reconnect_alive = consumer_register.consumer_conf['reconnect_alive']
        reconnect_count = consumer_register.consumer_conf['reconnect_count']
        ''' 重连计数，Consumer连接结果 '''
        c_count, c_result = 0, ''
        ''' 设置循环，进行连接重试 '''
        while c_count < reconnect_count:
            ''' 获取Consumer与注册中心的连接结果 '''
            c_result = consumer_connect.client_int({'type': 'get provider', 'fail_server': fail_server_list})
            ''' 等待一段时间后，再次重连 '''
            time_sleep(reconnect_alive)
            ''' 根据不同的返回类型，设置重连计数器 '''
            c_count = 1 if c_result == 'send fail' else (c_count + 1)
            print(f"[app] Consumer断线重连, 次数: {str(c_count)}。重试总次数: {str(reconnect_count)}，等待时长: {str(reconnect_alive)}")

    def __http_server__(self):
        """ 供 WEB 访问的简单 HTTP 服务启动 """
        # TODO 这里可以更换成 Flask 等，作为 WEB 服务器
        http_server(self.http_conf, self.http_services_class).serve_forever()


def main():
    """ 应用启动 """
    Thread(target=Application('configuration/profiles/app.yaml').__connect_link__).start()
    Thread(target=Application('configuration/profiles/app.yaml').__http_server__).start()


if __name__ == '__main__':
    main()
