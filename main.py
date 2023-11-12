import sys

from movie_app import MovieApp
from storage_json import StorageJson
from storage_csv import StorageCsv


def check_type(arg):
    if arg.endswith(".csv"):
        return StorageCsv(arg)
    return StorageJson(arg)


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        storage = check_type(arg)
        if not storage.file_exists():
            storage.create_file()
        movie_app = MovieApp(storage)
        movie_app.run()
        return
    print("Please provide the name of the storage file with the desired extension.")


if __name__ == '__main__':
    main()
