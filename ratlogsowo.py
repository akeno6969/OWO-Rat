import logging

logging.basicConfig(
    filename="logs/textlogowo.txt", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Bot started.")