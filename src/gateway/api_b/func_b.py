from eqsmart.main.remote_call import RemoteCall
from src.application.application import AC


def service(a, b):
    remote_response = RemoteCall('consumer_service_b/func_b').func_call(('b-a', 'b-b'))
    res = {
        'remote_b': remote_response,
        'api_b_func_b': str(a) + ' -- ' + str(b),
        'application_name': AC.read_conf('app.application.name')
    }
    return res
