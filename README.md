### 常见命令
- 开启前端：gradio gradio_app.py
- 数据库迁移：python manage.py makemigrations, python manage.py migrate
- 参考文档：https://www.gradio.app/docs/gradio/json

### 打标开源框架参考
1. https://github.com/opendatalab/LabelLLM
2. https://labelstud.io/guide/get_started
   * issue
   * [In Gradio , I want to define my own IP address at locally I don&#39;t want to use by default IP address · Issue #260 · gradio-app/gradio](https://github.com/gradio-app/gradio/issues/260)

## 换用MYSQL
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
