class Config(object):
    """ Basic configuration items. You can override or add any value in the corresponding location

    database_file = "<str>:database filename"
    replay_folder = "<str>:path to replays folder"
    json_file = "<str>:json filename"
    """
    
    DATABASE_FILE = "database.sqlite"
    REPLAY_FOLDER = "C:/Program Files (x86)/Steam/steamapps/common/Crypt of the NecroDancer/replays/"
    PRODUCTION = True

class DevelopmentConfig(Config):
    REPLAY_FOLDER = "replays/"
    DEBUG = False
    PRODUCTION = False

class ProductionConfig(Config):
    pass
