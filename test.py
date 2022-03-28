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

print(my_settings.default.timezone)
print(my_settings.system.name)
print(my_settings.system.step)

