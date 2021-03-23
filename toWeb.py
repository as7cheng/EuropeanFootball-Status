from flask import Flask, request, render_template, g, redirect, Response
import os


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/player')
def player():
    return render_template("palyer.html")
    
if __name__ == "__main__":
    app.run(debug=True)