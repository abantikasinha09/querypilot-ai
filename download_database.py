from pathlib import Path
from urllib.request import urlretrieve


DATABASE_URL = (
    "https://github.com/lerocha/chinook-database/raw/master/"
    "ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
)

DATABASE_PATH = Path(__file__).parent / "chinook.db"


def download_database():
    if DATABASE_PATH.exists():
        print("✅ chinook.db already exists.")
        return

    print("⬇️ Downloading Chinook database...")

    urlretrieve(DATABASE_URL, DATABASE_PATH)

    print(f"✅ Database downloaded to: {DATABASE_PATH}")


if __name__ == "__main__":
    download_database()