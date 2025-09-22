## SFT数据评估平台
用于json/markdown的数据渲染，供MUCFC业务人员阅览。
分数标注尚未实现。
### 常见命令
- password: $h0wmemOney
- 开启前端：`gradio gradio_app.py`
- 服务器开启服务：`nohup gradio gradio_app.py > runoob.log 2>&1 &` 在日志中检查输出
- 数据库迁移：`python manage.py makemigrations`, `python manage.py migrate`
- 参考文档：`https://www.gradio.app/docs/gradio/json`

### 打标开源框架参考
1. https://github.com/opendatalab/LabelLLM
2. https://labelstud.io/guide/get_started
   * issue
   * [In Gradio , I want to define my own IP address at locally I don&#39;t want to use by default IP address · Issue #260 · gradio-app/gradio](https://github.com/gradio-app/gradio/issues/260)
## 问题处理
#### linux命令快查
- 确认MySQL 服务是否存活`systemctl status mysqld`
- 重启MYSQL `sudo systemctl restart mysqld`
- 检查是否有进程监听7860端口 `ss -ltnp | grep 7860`
#### MYSQL连接超时
##### 可能1：
- Gradio 的调用间隔很长 → Django 长连接过期 → 再次使用时报 MySQL server has gone away。
解决办法就是：不要依赖长连接，而是在每次调用时重新建立连接。

- MySQL 服务器有一个名为 wait_timeout 的配置，它定义了服务器在关闭一个空闲连接之前等待的秒数。如果您的 Django 应用保持一个连接长时间未使用，超过了这个阈值，MySQL 服务器就会单方面断开连接。当 Django 再次尝试使用这个已经关闭的连接时，就会引发此错误。这在流量较低的网站或长时间运行的后台脚本中尤为常见。

- 您可以让 Django 在每次数据库操作前检查连接的存活时间。如果连接超过了指定的秒数，Django 会自动关闭并重新建立一个新的连接。[1][6][7]
关键点： CONN_MAX_AGE 的值应该设置得比 MySQL 的 wait_timeout 小。

##### 可能2：
- 有一个独立的脚本，通过 import django; django.setup() 来加载 Django 环境以使用 ORM。这种脚本的行为和管理命令类似，它不受 Django 的请求-响应周期管理。
- Gradio 不是 Django 请求： Gradio 的交互（例如，用户点击按钮）不会触发 Django 的请求/响应周期。因此，您设置的 'CONN_MAX_AGE': 0（即在每个请求后关闭连接）完全不起作用，因为从 Django 的角度来看，根本就没有“请求”发生。
- 因此需要在 Gradio 函数中手动管理连接：定义修饰器manage_db_connection(func)
#### TencentOS 没有安装好模块，需要手动安装并重新编译python
* `ModuleNotFoundError: No module named '_ssl'` Python 3.12 没有编译出 _ssl 模块，而 gradio 依赖 HTTPS，所以必须先解决这个问题。
#### 换用MYSQL
django.db.utils.NotSupportedError: SQLite 3.31 or later is required (found 3.26.0).
- 安装数据库服务器
```
sudo yum install -y mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
```
- 创建数据库
```
mysql -u root -p
CREATE DATABASE IF NOT EXISTS EvaluationData CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
- 修改 settings.py 的 DATABASES 配置
```
DATABASES = {
   "default": {
      "ENGINE": "django.db.backends.postgresql",
      "NAME": "数据库名字",
      "USER": "root",
      "PASSWORD": "", #root默认密码为空
      "HOST": "127.0.0.1",
      "PORT": "5432",
   }
}
```
- 安装 mysqlclient 失败原因是 缺少 MySQL 开发库和 pkg-config。需要编译
- 运行迁移 python manage.py migrate
