from configparser import ConfigParser

__all__ = [
    'BaseSettings',
    'BaseSection'
]


class SectionMetaClass(type):

    def __new__(mcs, name, bases, attrs):
        """
        检查不支持的注解类型
        """
        _super_new = super().__new__
        _supported_types = {
            str: 'str',
            int: 'int',
            float: 'float',
            bool: 'bool',
            list: 'list'
        }
        # 没有注解的需要添加
        if not hasattr(mcs, '__annotations__'):
            setattr(mcs, '__annotations__', {})

        attrs['_supported_types'] = _supported_types
        for attr, val in mcs.__annotations__.items():
            if val not in _supported_types:
                _types = ', '.join(map(lambda t: t.__name__, _supported_types))
                raise AttributeError(
                    f"The type '{val}' for '{attr}' is not supported by settings. "
                    f"Supported types are {_types}."
                )

        return _super_new(mcs, name, bases, attrs)


class BaseSection(object, metaclass=SectionMetaClass):
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
    _allow_undefined = True  # 是否允许未定义的属性

    def __init__(self, allow_undefined=None):
        """
        allow_undefined: 是否允许读取未定义配置项（如果存在，默认转为字符串）
        """
        self._section_name = self.__class__.__name__
        if allow_undefined is not None:
            self._allow_undefined = allow_undefined

    def __getattr__(self, key):
        """
        通过注解类型获取配置的值
        """
        options = self.__annotations__
        option_keys = options.keys()
        section_name = self.__class__.__name__
        if key not in option_keys:
            if self._allow_undefined:
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
                # type changing
                type_name = self._supported_types.get(a_type)
                try:
                    # try to get the self defined method
                    return object.__getattribute__(self, 'to_' + type_name).__call__(value)
                except AttributeError:
                    pass

                if value is None:
                    return value
                # default action
                return a_type.__call__(value)
        return super().__getattribute__(key)

    def __repr__(self):
        return '<%s section object>' % self.__class__.__name__

    def __dict__(self):
        dirs = dict()
        for key, value in self.__annotations__.items():
            dirs[key] = getattr(self, key)
        return dirs

    def add_supported_type(self, _type, type_name):
        assert isinstance(type_name, str)
        self._supported_types.update({_type: type_name})

    @staticmethod
    def to_bool(value: str):
        if value in ('true', 'True'):
            return True
        elif value in ('false', 'False'):
            return False
        raise TypeError


class BaseSettings(object):
    path = None

    def __new__(cls, *args, **kwargs):
        assert cls.path is not None, "The attribute 'path' must be given."
        parser = ConfigParser()
        parser.read(cls.path)
        dicts = filter(
            lambda item: not item[0].startswith('__') and isinstance(item[1], BaseSection),
            cls.__dict__.items())
        for attr, obj in dicts:
            setattr(obj, '_parser', parser)
        return super().__new__(cls, *args, **kwargs)

    def __dir__(self):
        dirs = super().__dir__()
        dirs = [item for item in dirs
                if not item.startswith('_')
                and isinstance(getattr(self, item), BaseSection)]
        return dirs

    def __iter__(self):
        dirs = self.__dir__()
        for item in dirs:
            yield getattr(self, item).__dict__()

    def __repr__(self):
        return '<%s settings object>' % self.__class__.__name__
