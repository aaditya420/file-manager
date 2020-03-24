import os
import sys
import time
import json
import logging
import argparse
from watchdog.utils import has_attribute
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(
                "debug.log",
                "a"
            ),
            logging.StreamHandler()
        ]
    )
except Exception as e:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(
                "debug.log",
                "w"
            ),
            logging.StreamHandler()
        ]
    )

parser = argparse.ArgumentParser(description="Monitor a particular folder for file changes and sort them based on the config.json")

parser.add_argument(
    '-wd', '--watchDirectory',
    type=str,
    default=".",
    help="The directory to watch for changes"
)
parser.add_argument(
    '-c', '--config',
    type=str,
    default="config.json",
    help="Config file location"
)
parser.add_argument(
    '-i', '--interval',
    type=int,
    default=2,
    help="Interval in seconds to sleep the monitoring threads"
)

class MonitorFolder(FileSystemEventHandler):

    def __init__(self, watchDirectory=".", config="config.json", interval=5, observer=Observer()):
        self.watchDirectory = watchDirectory
        self.config = config
        self.interval = interval
        self.observer = observer

        self.filename = ""
        self.include = json.load(open(self.config))["include"]
        self.ignore = json.load(open(self.config))["ignore"]
        self.others = json.load(open(self.config))["others"]

    def on_moved(self, event):
        super(MonitorFolder, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

        if what == 'file':
            self.organize(event)

    def on_created(self, event):
        super(MonitorFolder, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)

        self.organize(event)

    def on_deleted(self, event):
        super(MonitorFolder, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(MonitorFolder, self).on_modified(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)

    def organize(self, event):
        if has_attribute(event, 'dest_path'):
            file_path = event.dest_path
        else:
            file_path = event.src_path

        what = 'directory' if event.is_directory else 'file'
        if what == "file":
            self.filename = file_path.split("\\")[-1]
            assigned_folder = self.assign_folder(what)
            if assigned_folder is None:
                return
        elif what == "directory":
            self.filename = file_path.split("\\")[-1]
            assigned_folder = self.assign_folder(what)

        try:
            os.rename(
                file_path,
                os.path.join(
                    assigned_folder,
                    self.filename
                )
            )

        except FileExistsError as e:
            logging.exception(e)
            logging.error("File already exists. Cleaning up.")
            os.remove(file_path)

        except NotImplementedError as e:
            logging.exception(e)
            logging.debug(f"Creating directory - {assigned_folder}...")
            os.mkdir(assigned_folder)
            os.rename(
                file_path,
                os.path.join(
                    assigned_folder,
                    self.filename
                )
            )

    def assign_folder(self, what="file"):
        self.include = json.load(open(self.config))["include"]
        self.ignore = json.load(open(self.config))["ignore"]
        self.others = json.load(open(self.config))["others"]

        if what == 'file':
            extension = self.filename.split(".")[-1].lower()
            logging.info(f"File extension - {extension}")
            if extension not in self.ignore:
                try:
                    logging.debug(
                        f"Folder assigned - {self.include[extension]}")
                    return self.include[extension]
                except Exception as e:
                    logging.exception(e)
                    logging.error(
                        "File extension not handled, using default folder.")
                    return self.others
            else:
                logging.info("Extension ignored.")
                return None

        if what == 'directory':
            dir_info = [
                folder for folder in os.walk(
                    os.path.join(
                        self.watchDirectory,
                        self.filename
                    )
                )
            ]
            extensions = {}

            for dirs in dir_info:
                files = dirs[-1]
                for file in files:
                    extension = file.split(".")[-1]
                    if extension in extensions.keys():
                        extensions[extension] += 1
                    else:
                        extensions[extension] = 0

            try:
                extension = max(extensions, key=extensions.get)
                logging.info(f"File extension - {extension}")
            except Exception as e:
                logging.exception(e)
                time.sleep(10)
                return self.assign_folder(what)

            try:
                logging.debug(f"Folder assigned - {self.include[extension]}")
                return self.include[extension]
            except Exception as e:
                logging.exception(e)
                logging.error(
                    "File extension not handled, using default folder.")
                return self.include[MonitorFolder.OTHERS]

    def run(self):

        logging.debug("Loading scheduler...")
        self.observer.schedule(
            self,
            self.watchDirectory
        )
        logging.info("Scheduler loaded!")

        logging.debug("Starting observer...")
        self.observer.start()
        logging.info("Observer started!")

        try:
            while True:
                time.sleep(self.interval)
        except Exception as e:
            self.observer.stop()
            logging.exception(e)
            logging.info("Observer Stopped.")

        self.observer.join()


if __name__ == "__main__":
    env = ""
    try:
        logging.debug("Parsing arguments...")
        args = vars(parser.parse_args(sys.argv[1:]))
        logging.info("Arguments parsed!")
    except Exception as e:
        logging.exception(e)
        logging.error("Sorry, unable to prase arguments :(")
        parser.print_help()
    
    MonitorFolder(**args).run()
