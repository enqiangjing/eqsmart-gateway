from eqsmart.main.remote_call import RemoteCall
from src.application.application import AC


def service(a, b):
    remote_response = RemoteCall('consumer_service_a/func_a').func_call(('a-a', 'a-b'))
    res = {
        'remote_a': remote_response,
        'api_a_func_a': str(a) + ' -- ' + str(b),
        'application_name': AC.read_conf('app.application.name')
    }
    return res
