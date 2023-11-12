import json
import os

from istorage import IStorage


class StorageJson(IStorage):
    def __init__(self, file_path):
        self.file_path = file_path

    def list_movies(self):
        try:
            with open(self.file_path, "r") as file:
                movies_data = json.load(file)
            if movies_data:
                return movies_data
            return {}
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def add_movie(self, name, year, rating, poster):
        try:
            movies_data = self._read_file()
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            movies_data = {}
        movies_data[name] = {
            "rating": rating,
            "year": year,
            "poster": poster
        }
        self._write_file(movies_data)

    def delete_movie(self, title):
        try:
            movies_data = self._read_file()
        except FileNotFoundError:
            return
        del movies_data[title]
        self._write_file(movies_data)

    def update_movie(self, name, note):
        try:
            movies_data = self._read_file()
        except FileNotFoundError:
            return
        if name in movies_data:
            movies_data[name]["note"] = note
            self._write_file(movies_data)

    def _read_file(self):
        with open(self.file_path, "r") as file:
            return json.load(file)

    def _write_file(self, data):
        with open(self.file_path, "w") as file:
            json.dump(data, file)

    def file_exists(self):
        return os.path.exists(self.file_path)

    def create_file(self):
        with open(self.file_path, 'w') as file:
            json.dump({}, file)
