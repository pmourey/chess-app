# config.py
import os

class Config:
    DEBUG = True
    SECRET_KEY = 'fifa 2022'
    BASE_PATH = os.path.dirname(__file__)
    ENGINES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engines', 'stockfish')
    LICHESS_API_URL = "https://lichess.org/api"
    LICHESS_API_TOKEN = os.getenv('LICHESS_API_TOKEN')

