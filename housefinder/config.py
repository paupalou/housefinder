import yaml


class Provider(object):
    def __init__(self, provider_number):
        with open("personal_config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            self.info = cfg['providers'][provider_number]

    def get(self, property):
        return self.info[property]


class GoogleCredentials(object):
    def __init__(self):
        with open("personal_config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            self.info = cfg['google_credentials']

    def get(self, property):
        return self.info[property]
