from pathlib import Path
import shutil
import zipfile
import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

DOWNLOADS_PATH = Path(r"C:\Users\KubaS\Downloads")
DOCUMENTS_PATH = Path(r"C:\Users\KubaS\Documents")
IMAGES_PATH = Path(r"C:\Users\KubaS\Pictures")
MUSIC_PATH = Path(r"C:\Users\KubaS\Music")
SCHOOL_PATH = DOCUMENTS_PATH / "skola"
VIDEOS_PATH = Path(r"C:\Users\KubaS\Videos")
DESTINATIONS = {
    ".pdf": DOCUMENTS_PATH / "pdf/",
    ".msi": DOCUMENTS_PATH / "installers/",
    ".exe": DOCUMENTS_PATH / "installers/",
    ".zip": DOCUMENTS_PATH / "unzipped/",
    "school.zip": SCHOOL_PATH / "unzipped/",
    "global": DOCUMENTS_PATH / "unsorted/",
    ".png": IMAGES_PATH,
    ".jpg": IMAGES_PATH,
    ".jpeg": IMAGES_PATH,
    ".gif": IMAGES_PATH,
    ".mp3": MUSIC_PATH,
    ".waw": MUSIC_PATH,
    ".webp": IMAGES_PATH,
    ".mp4": VIDEOS_PATH,
    ".avi": VIDEOS_PATH,
    ".mov": VIDEOS_PATH,
}

class FileMover(FileSystemEventHandler):
    def __init__(self, destinations: dict[str, Path], dl_path: Path):
        self._destinations = destinations

        _init_items = os.listdir(dl_path)
        for item in _init_items:
            self.process(dl_path / item)

    def _react_to_file_event(self, event):
        fpath = event.src_path
        if fpath.endswith(".tmp"):
            return
        self.process(Path(fpath))

    def on_modified(self, event):
        self._react_to_file_event(event)

    def on_created(self, event):
        self._react_to_file_event(event)

    def process(self, fpath: Path):
        if not os.path.exists(fpath):
            return
        file_name = fpath.name
        processed: bool = False
        for filter_keyword, destination in self._destinations.items():
            if filter_keyword in file_name:
                if filter_keyword == ".zip":
                    stem = fpath.stem
                    unzip_dest = self._destinations[".zip"] if not ("hw" in stem or "assignment" in stem)\
                        else self._destinations["school.zip"]
                    unzip_dest = Path(unzip_dest) / stem
                    self.unzip_to(fpath, unzip_dest)
                    os.remove(fpath)
                else:
                    os.makedirs(destination, exist_ok=True)
                    print(f"Moving {file_name} to {destination}")
                    shutil.move(fpath, destination)
                processed = True
                break

        if not processed:
            os.makedirs(self._destinations["global"], exist_ok=True)
            print(f"Moving {file_name} to {self._destinations["global"]}")
            shutil.move(fpath, self._destinations["global"])

    def unzip_to(self, zip_path: Path, destination: Path):
        os.makedirs(destination, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:

            zip_ref.extractall(destination)
            print(f"Extracted all files to: {destination}")


def run():
    move_handler = FileMover(destinations=DESTINATIONS, dl_path=DOWNLOADS_PATH)
    observer = Observer()
    observer.schedule(move_handler, path=DOWNLOADS_PATH, recursive=False)
    observer.start()

    print("Watching for new files in Downloads...")

    try:
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == '__main__':
    run()
