from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/waytodashboard/<mail>', methods=['GET', 'POST'])
def waytodashboard(mail):
    
    print(mail)
    return render_template('dashboard.html', useremail = mail)


if __name__ == '__main__':
    app.run()
