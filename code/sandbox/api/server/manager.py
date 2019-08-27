"""
Manager
"""

from flask_script import Manager # pylint: disable=E0401
from application import APP

manager = Manager(APP)

if __name__ == "__main__":
    manager.run()
