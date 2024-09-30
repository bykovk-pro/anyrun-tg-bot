import logging

class Config:
    def __init__(self, env_vars):
        self.env_vars = env_vars

    def get(self, key, default=None):
        return self.env_vars.get(key, default)

    def get_log_level(self, key='LOG_LEVEL'):
        log_level = self.get(key, 'INFO')
        return getattr(logging, log_level.upper(), logging.INFO)

def create_config(env_vars):
    return Config(env_vars)