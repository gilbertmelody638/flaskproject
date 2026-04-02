from os import environ
from FlaskWebProject import app

if __name__ == "__main__":
    host = environ.get("HOST", "0.0.0.0")
    port = int(environ.get("PORT", 8000))
    app.run(host=host, port=port)