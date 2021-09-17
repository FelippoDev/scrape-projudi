from flask import Flask, render_template, request
import scraper
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        token = request.form['token']
        scraper.main(token)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

