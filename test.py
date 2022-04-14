import os

from core import BaseSection, BaseSettings


class DEFAULT(BaseSection):
    timezone: str


class System(BaseSection):
    # name: str  # allow_undefined为True时，str类型可以不定义
    idle_seconds: int
    debug: bool = False  # 支持默认值
    step: float


class MySettings(BaseSettings):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings_sample.ini')
    default = DEFAULT()
    system = System(allow_undefined=True)


my_settings = MySettings()

# 调用1
print(my_settings.default.timezone)

# 调用2
default = my_settings.default
print(default.timezone)

# 某个section所有配置
print(my_settings.system.__dict__())

# 所有的配置
for item in my_settings:
    print(item)
