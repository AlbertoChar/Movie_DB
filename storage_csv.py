import csv

from istorage import IStorage


class StorageCsv(IStorage):
    def __init__(self, file_path):
        self.file_path = file_path

    def list_movies(self):
        try:
            with open(self.file_path, "r", newline='') as file:
                reader = csv.DictReader(file)
                movies_data = {row["name"]: row for row in reader}
            if movies_data:
                return movies_data
            return {}
        except (FileNotFoundError, csv.Error):
            return {}

    def add_movie(self, name, year, rating, poster):
        movies_data = self.list_movies()
        movies_data[name] = {
            "name": name,
            "rating": rating,
            "year": year,
            "poster": poster
        }
        self._write_file(movies_data)

    def delete_movie(self, title):
        movies_data = self.list_movies()
        del movies_data[title]
        self._write_file(movies_data)

    def update_movie(self, name, note):
        movies_data = self.list_movies()
        if name in movies_data:
            movies_data[name]["note"] = note
            self._write_file(movies_data)

    def _write_file(self, data):
        fieldnames = ["name", "year", "rating", "poster", "note"]  # Adjust field names as needed
        with open(self.file_path, "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data.values())
