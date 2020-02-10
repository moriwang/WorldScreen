## 环球银幕杂志下载
使用 python 自动获取当期杂志页数，下载，合并PDF。

针对可能出现压缩包无法解压的情况，增加了一次自动重试。

### 效果
![image](https://github.com/moriwang/WorldScreen/blob/master/img/20200210-131056.jpg)

### 使用方法
首先需要取得格式如 'XX/XXX/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' 的下载路径。

由于版权原因，本仓库不予提供，如有兴趣，可下载 iPad 版「环球银幕HD」App 自行研究取得。
经测试，iPadOS 13.3 已无法运行。

在 [config.py](https://github.com/moriwang/WorldScreen/blob/master/config.py) 中填入下载路径后，
运行 [main.py](https://github.com/moriwang/WorldScreen/blob/master/main.py) 即可取得该期杂志。

### 技术分析
杂志的预览图压缩包提供了实现了自动取得页码与真实下载链接的基础。

使用 requests 模拟 App 客户端 Header，并简单实现了一个多线程下载器。

解压后将文件进行不同策略的处理后，使用 PyPDF2 合并。

### License
See the LICENSE file for license rights and limitations (MIT).
