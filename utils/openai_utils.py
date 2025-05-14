import os

class ProxyContext:
    def __init__(self, env_vars=None):
        if env_vars is None:
            env_vars = {'HTTP_PROXY', 'HTTPS_PROXY'}
        self.env_vars = env_vars
        self.saved_values = {}

    def __enter__(self):
        # 保存指定环境变量的值，并删除它们
        for var_name in self.env_vars:
            self.saved_values[var_name] = os.environ.get(var_name, '')
            os.environ.pop(var_name, None)

    def __exit__(self, exc_type, exc_value, traceback):
        # 在需要时将环境变量恢复
        for var_name, value in self.saved_values.items():
            os.environ[var_name] = value
