import os
from configparser import NoOptionError, ConfigParser

from utils import str2bool


class BaseConverter:

    def to_python(self, value):
        raise NotImplementedError


class BoolConverter(BaseConverter):

    def to_python(self, value):
        return str2bool(value)


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

    def __init__(self, allow_undefined=None):
        """
        allow_undefined: 是否允许读取未定义配置项（如果存在，默认转为字符串）
        """
        self._section_name = self.__class__.__name__
        if allow_undefined is not None:
            self.allow_undefined_options = allow_undefined

    def __getattr__(self, key):
        """
        通过注解类型获取配置的值
        """
        options = self.__annotations__
        option_keys = options.keys()
        section_name = self.__class__.__name__
        if key not in option_keys:
            if self.allow_undefined_options:
                # build undefined option
                options[key] = str
            else:
                raise AttributeError("No option '%s' defined in section %s." % (key, section_name))
        for option, a_type in options.items():
            if key == option:
                try:
                    value = self._parser.get(section_name, option)
                except Exception as e:
                    raise e
                if a_type is bool:
                    return str2bool(value)
                if value is None:
                    return value
                return a_type.__call__(value)
        return super().__getattribute__(key)

    def __new__(cls, *args, **kwargs):
        """
        检查不支持的注解类型
        """
        _super_new = super().__new__
        # 没有注解的需要添加
        if not hasattr(cls, '__annotations__'):
            setattr(cls, '__annotations__', {})
        _supported_types = (str, int, float, bool, list)
        for attr, val in cls.__annotations__.items():
            if val not in _supported_types:
                _types = ', '.join(map(lambda t: t.__name__, _supported_types))
                raise AttributeError(
                    f"The type '{val}' for '{attr}' is not supported by settings. "
                    f"Supported types are {_types}."
                )
        return _super_new(cls)

    def __repr__(self):
        return '<%s section object>' % self.__class__.__name__


class BaseSettings(object):
    path = None

    def __new__(cls, *args, **kwargs):
        assert cls.path is not None, "The attribute 'path' must be given."
        if not os.path.exists(cls.path):
            raise AttributeError(f"The path {cls.path} does not exist.")
        parser = ConfigParser()
        parser.read(cls.path)
        dicts = filter(
            lambda item: not item[0].startswith('__') and isinstance(item[1], BaseSection),
            cls.__dict__.items())
        for attr, obj in dicts:
            setattr(obj, '_parser', parser)
        return super().__new__(cls, *args, **kwargs)
