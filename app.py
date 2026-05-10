from flask import Flask, render_template

app = Flask(__name__) # 建立application 物件

# 建立網站首頁的回應方式
@app.route("/")
def index(): # 用來回應網站首頁連結的函式
    return render_template('index.html')

# 啟動網站伺服器
if __name__=="__main__":
    app.run(debug=True)