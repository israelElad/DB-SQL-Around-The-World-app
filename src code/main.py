from controller.db_manager import DataBaseManager
from database.database import Database
from gui.gui_run import MainGUI
from database.config import *

db = Database()
db.initialize()
db_manager = DataBaseManager(db)
gui = MainGUI(db_manager)
gui.run()
db.close()