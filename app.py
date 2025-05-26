import os

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from src.apis.camapi import blueprint as camapi
from src.apis.accountapi import blueprint as accountapi
from src.database.sql_manager import init_mysql
from src.global_data.config import init_config

init_config()
init_mysql()

app = Flask(__name__)
CORS(app)  # 配置跨域

# 注册蓝图
app.register_blueprint(camapi, url_prefix='/api/cameras')
app.register_blueprint(accountapi, url_prefix='/api/users')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    app.run(debug=True, port=8080)
