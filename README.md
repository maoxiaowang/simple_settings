# Simple Settings

## 使用说明
通过类名和section，属性和option对应的方式

### 配置文件示例如下
```ini
[DEFAULT]
timezone = Asia/Shanghai

[System]
name = test
idle_seconds = 60
debug = true
step = 0.1
```

### 自定义Section类，如下
```python
from simple_settings import BaseSection

class DEFAULT(BaseSection):
    timezone: str


class System(BaseSection):
    # name: str  # allow_undefined为True时，str类型可以不定义
    idle_seconds: int
    debug: bool
    step: float
```

> 说明：类名对应配置文件的section名，类注解对应option， 
> 注解目前支持固定的类型，str, int, float, bool, list。

### 继承并构建配置类
```python
from simple_settings.core import BaseSettings

class MySettings(BaseSettings):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings_sample.ini')
    default = DEFAULT()
    system = System(allow_undefined=False)  # 不允许配置文件里没有的选项
```

### 在项目中使用
```python
my_settings = MySettings()

my_settings.default.timezone
my_settings.system.name
my_settings.system.step
```
