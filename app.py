from flask import Flask, render_template
from routes.analyze_code import analyze_code_bp
from routes.submit_practice import submit_practice_bp
from routes.chat import chat_bp
from routes.compiler import compiler_bp   # NEW

app = Flask(__name__)

# Register blueprints
app.register_blueprint(analyze_code_bp, url_prefix="/analyze")
app.register_blueprint(submit_practice_bp, url_prefix="/practice")
app.register_blueprint(chat_bp, url_prefix="/chat")
app.register_blueprint(compiler_bp, url_prefix="/compiler")    # NEW


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)