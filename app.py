from flask import Flask, render_template
from flask_cors import CORS
from apis.camapi import blueprint as camapi

app = Flask(__name__)
CORS(app)  # 配置跨域

# 注册蓝图
app.register_blueprint(camapi, url_prefix='/api/cameras')

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True, port=8080)
