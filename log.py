from time import strftime


def LOGE(info):
    print('[%s] \033[91m[ERROR]\033[0m%s\n' % (strftime('%H:%M:%S'), info))


def LOGW(info):
    print('\033[93m[%s]%s\033[0m\n' % (strftime('%H:%M:%S'), info))


def LOGS(info):
    print('\033[92m[%s]%s\033[0m\n' % (strftime('%H:%M:%S'), info))


def yecho(info): print(f"\033[36m[{strftime('%H:%M:%S')}]{info}\033[0m")


def ywarn(info): print(f"\033[31m{info}\033[0m")
