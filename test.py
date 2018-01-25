from src.swtools.gerrit import Gerrit
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
gerrit = Gerrit("wall", "user", "password")
gerrit.print_info()