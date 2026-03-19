import sys
from pathlib import Path
import tempfile
import urllib.request
import shutil
import zipfile

def get_server(argv):
    if argv[1] in {"us", "eu"}:
        return argv[1]
    else:
        return None

def get_path(argv):
    steam_library = Path(argv[2]).expanduser()

    if not steam_library.exists():
        return None

    pfx_path = steam_library / "steamapps" / "compatdata" / "306130" / "pfx"

    if not pfx_path.exists():
        return None

    ttc_path = (
        pfx_path
        / "drive_c"
        / "users"
        / "steamuser"
        / "My Documents"
        / "Elder Scrolls Online"
        / "live"
        / "AddOns"
        / "TamrielTradeCentre"
    )

    # создаем если не существует
    ttc_path.mkdir(parents=True, exist_ok=True)

    return ttc_path

def download_ttc_db(server):
    urls = {
        "eu": "https://eu.tamrieltradecentre.com/download/PriceTable",
        "us": "https://us.tamrieltradecentre.com/download/PriceTable",
    }

    if server not in urls:
        return None

    tmp_dir = Path(tempfile.mkdtemp(prefix="ttc_"))
    archive_path = tmp_dir / "PriceTable.zip"

    try:
        with urllib.request.urlopen(urls[server], timeout=60) as response:
            if response.status != 200:
                return None

            archive_path.write_bytes(response.read())

    except Exception:
        return None

    return archive_path

def add_new_db(ttc_path: Path, new_db_path: Path) -> bool:
    if not zipfile.is_zipfile(new_db_path):
        return False

    extract_dir = new_db_path.parent / "extract"
    extract_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(new_db_path, "r") as archive:
            archive.extractall(extract_dir)

        new_lua_files = list(extract_dir.rglob("*.lua"))
        if not new_lua_files:
            return False

        for lua_file in new_lua_files:
            old_file = ttc_path / lua_file.name
            if old_file.exists():
                old_file.unlink()

        for lua_file in new_lua_files:
            shutil.copy2(lua_file, ttc_path / lua_file.name)

    except Exception:
        return False

    return True

def main(argv):
    argv_correct_length = 3
    if len(argv) != argv_correct_length:
        print("is not correct length")
        return
    
    server = get_server(argv)
    if server is None:
        print("is not correct server")
        return
    
    gamedata_path = get_path(argv)
    if gamedata_path is None:
        print("is not correct path")
        return
    
    ttc_db_path = download_ttc_db(server)
    if ttc_db_path is None:
        print("download error")
        return
    
    result = add_new_db(gamedata_path, ttc_db_path)

    if result is True:
        print("success")
    else:
        print("unsucces add db")
    

if __name__ == "__main__":
    main(sys.argv)