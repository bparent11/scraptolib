import time, random, logging

def human_delay(lowest:int=5, low:int=1, high:int=2, alpha:float=1):
    time.sleep(random.uniform(min(low, lowest), high*alpha))

def init_logger():
    lg = logging.getLogger(__name__)
    lg.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Format optionnel
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Ajouter le handler au logger
    lg.addHandler(console_handler)

    return lg