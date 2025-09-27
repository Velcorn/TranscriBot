from configparser import ConfigParser

# Full path to config file
path = './config.ini'
section = 'config'


def config():
    parser = ConfigParser()
    parser.read(path)
    api = {}
    params = parser.items(section)
    for param in params:
        api[param[0]] = param[1]
    return api
