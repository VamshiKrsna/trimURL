from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import string
import random
import pyperclip

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = create_engine('sqlite:///urls.db', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class URL(Base):
    __tablename__ = 'urlslist'
    id = Column(Integer, primary_key=True)
    long_url = Column(String)
    short_url = Column(String)

    def init(self,long_url,short_url):
        self.long_url = long_url
        self.short_url = short_url

    def __repr__(self):
        return f"<URL(id={self.id}, long_url='{self.long_url}', short_url='{self.short_url}')>"

Base.metadata.create_all(engine)

@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None
    if request.method == 'POST':
        long_url = request.form['long_url']
        short_url = shorten_url()
        url = URL(long_url=long_url, short_url=short_url)
        db_session = Session()
        db_session.add(url)
        db_session.commit()
        db_session.close()
    return render_template('home.html', short_url=short_url)

@app.route('/')
def copy_to_clipboard(url):
    short_url = shorten_url(url)
    full_url = f"http://{request.host}/{short_url}/{url}"
    pyperclip.copy(full_url)

@app.route('/history')
def history():
    db_session = Session()
    urls = db_session.query(URL).all()
    db_session.close()
    return render_template('history.html', urls=urls)

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    db_session = Session()
    url = db_session.query(URL).filter_by(short_url=short_url).first()
    db_session.close()
    if url:
        return redirect(url.long_url)
    else:
        return render_template('404.html')

def shorten_url():
    chars = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(chars) for _ in range(6))
    db_session = Session()
    while db_session.query(URL).filter_by(short_url=short_url).first() is not None:
        short_url = ''.join(random.choice(chars) for _ in range(6))
    db_session.close()
    temp_url = f"http://{request.host}/{short_url}"
    return short_url

def copy_to_clipboard(url):
    short_url = shorten_url(url)
    full_url = f"http://{request.host}/{short_url}/{url}"
    pyperclip.copy(full_url)

def history():
    return render_template('history.html')

if __name__ == '__main__':
    app.run(debug=True)
