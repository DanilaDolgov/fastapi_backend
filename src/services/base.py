from src.utils.s3_manager import S3Manager
from src.utils.db_manager import DBManager



class BaseServices:
    db: DBManager | None
    s3: S3Manager | None

    def __init__(self, db: DBManager | None = None, s3: S3Manager | None = None) -> None:
        self.db = db
        self.s3 = s3