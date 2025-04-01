from rat.app import app

application = app  # Gunicorn'un arayacağı isim

if __name__ == "__main__":
    application.run()
