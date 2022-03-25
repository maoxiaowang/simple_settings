"""
############# 使用说明 #############

# 配置文件示例如下
[DEFAULT]
timezone = Asia/Shanghai

[System]
name = test
idle_seconds = 60
debug = true
step = 0.1

# 自定义Section类，如下
from simple_settings import BaseSection

class DEFAULT(BaseSection):
    timezone: str


class System(BaseSection):
    idle_seconds: int
    debug: bool
    step: float

# 说明：类名对应配置文件的section名，类注解对应option，
# 注解目前支持固定的类型，str, int, float, bool, list

# 继承并构建配置类
from simple_settings.core import BaseSettings

class MySettings(BaseSettings):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings_sample.ini')
    default = DEFAULT()
    system = System()

# 在项目中使用
my_settings = MySettings()
my_settings.default.timezone
my_settings.system.step

"""
import os
from configparser import NoOptionError, ConfigParser

from utils import str2bool


class BaseSection(object):
    """
    配置文件里section的名字要与类名一致
    如：
    [Mariadb]
    host=127.0.0.1

    class Mariadb:
        pass

    注意：定义的option（属性名）不要以下划线开头
    """
    _parser = None
    allow_undefined_options = True

    def __init__(self, allow_undefined):
        """
        allow_undefined: 是否允许读取未定义配置项（如果存在，默认转为字符串）
        """
        self.allow_undefined_options = allow_undefined

    def __getattr__(self, item):
        """
        未定义的属性通过注解类型获取配置的值
        """
        print(item)
        section_name = self.__class__.__name__
        options = self.__annotations__
        option_keys = options.keys()
        if item not in option_keys:
            if self.allow_undefined_options:
                # build undefined option
                options[item] = str
            else:
                raise AttributeError(
                    "No option '%s' defined in section %s." % (item, section_name)
                )
        for option, type_val in options.items():
            if item == option:
                value = self._parser.get(section_name, option)
                if type_val is bool:
                    return str2bool(value)
                if type_val is list:
                    return value.split(',')
                if value is None:
                    return value
                return type_val.__call__(value)
        return super().__getattribute__(item)

    def __getattribute__(self, item):
        """
        section属性有赋值
        """
        if item.startswith('_'):
            # 以下划线开头的属性直接返回
            return object.__getattribute__(self, item)
        try:
            section_name = self.__class__.__name__
            value = self._parser.get(section_name, item)
        except NoOptionError:
            # 配置文件中没有配置，返回默认值
            return item
        else:
            return value

    def __new__(cls, *args, **kwargs):
        """
        检查不支持的注解类型
        """
        _super_new = super().__new__
        # 没有注解的需要添加
        if not hasattr(cls, '__annotations__'):
            setattr(cls, '__annotations__', {})
        supported_types = (str, int, float, bool, list)
        for attr, val in cls.__annotations__.items():
            if val not in supported_types:
                _types = ', '.join(map(lambda t: t.__name__, supported_types))
                raise AttributeError(
                    f"The type '{val}' for '{attr}' is not supported by settings. "
                    f"Supported types are {_types}."
                )
        return _super_new(cls)

    def __repr__(self):
        return '<%s settings object>' % self.__class__.__name__


class BaseSettings(object):
    path = None

    def __new__(cls, *args, **kwargs):
        assert cls.path is not None, "The attribute 'path' must be given."
        if not os.path.exists(cls.path):
            raise AttributeError(f'The path {cls.path} does not exist.')
        parser = ConfigParser()
        parser.read(cls.path)
        dicts = filter(
            lambda item: not item[0].startswith('__') and isinstance(item[1], BaseSection),
            cls.__dict__.items())
        for attr, obj in dicts:
            setattr(obj, '_parser', parser)
        return super().__new__(cls, *args, **kwargs)
