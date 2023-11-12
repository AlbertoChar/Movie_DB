import random
import requests
from fuzzywuzzy import fuzz

from storage_json import StorageJson

# ANSI escape codes for text color
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

API_KEY = "648d93c2"
API = f"http://www.omdbapi.com/?apikey={API_KEY}&t="


def print_colored(text, color):
    print(color + text + RESET)


def replace_in_html(html_file, target_text, replacement_text):
    full_path = f"_static/{html_file}"
    with open(full_path, 'r') as file:
        html_content = file.read()

    modified_html = html_content.replace(target_text, replacement_text)
    with open(full_path, 'w') as file:
        file.write(modified_html)


def serialize_movie(title, details):
    output = "<li>\n"
    output += "<div class='movie' title='"
    if 'note' in details and details['note']:
        output += f"{details['note']}"
    output += "'>\n"
    output += f"<img class='movie-poster' src={details['poster']}/>\n"
    output += f"<div class='movie-title'>{title}</div>\n"
    output += f"<div class='movie-year'>{details['year']}</div>\n"
    output += "</div>\n"
    output += "</li>\n"
    return output


def calc_av(movies):
    av = 0
    total_rating = 0
    num_movies = len(movies)
    if num_movies == 0:
        return 0
    for movie in movies.values():
        total_rating += float(movie["rating"])
    av = total_rating / num_movies
    return av


def calc_med(movies):
    ratings = [float(movie["rating"]) for movie in movies.values()]
    sorted_ratings = sorted(ratings)
    number_ratings = len(ratings)
    if number_ratings % 2 == 0:
        middle1 = sorted_ratings[number_ratings // 2 - 1]
        middle2 = sorted_ratings[number_ratings // 2]
        median = (middle1 + middle2) / 2
        return median
    median = sorted_ratings[number_ratings // 2]
    return median


def get_best(movies):
    best_rating = max(float(movie["rating"]) for movie in movies.values())
    best_movies = [title for title, movie in movies.items() if movie["rating"] == best_rating]
    return best_movies, best_rating


def get_worst(movies):
    worst_rating = min(float(movie["rating"]) for movie in movies.values())
    worst_movies = [title for title, movie in movies.items() if movie["rating"] == worst_rating]
    return worst_movies, worst_rating


def menu():
    print()
    print_colored("** Welcome to my movies database **", GREEN)
    print()
    print("Menu:")
    print("1. List movies")
    print("2. Add movie")
    print("3. Delete movie")
    print("4. Update movie")
    print("5. Stats")
    print("6. Random movie")
    print("7. Search movie")
    print("8. Movies sorted by rating")
    print("9. Generate Website")
    print("0. Exit")
    print()
    print("Enter choice (1-8)")
    choice = input()
    return int(choice)


class MovieApp:
    def __init__(self, storage):
        self._storage = storage

    def list_movies(self):
        movies = self._storage.list_movies()
        if movies:
            print_colored(f"{len(movies)} in total:", GREEN)
            for movie, details in movies.items():
                print(f"{movie}, Year: {details['year']}")
            return
        print_colored("No movies in the database", YELLOW)
        return

    def add_movie(self):
        movies = self._storage.list_movies()
        print("Enter the movie name you would like to add:")
        name = input()
        if not name:
            print_colored("Title is required.", RED)
            return
        if name in movies:
            print_colored(f"Movie {name} already in database!", YELLOW)
            return
        url = API + name
        response = requests.get(url)
        if response.status_code == 200:
            self.fetch_movie(response)
            return
        print_colored("There seems to be an error, please try again", RED)

    def fetch_movie(self, response):
        movie_data = response.json()
        name = movie_data.get("Title")
        year = movie_data.get("Year")
        rating = movie_data.get("imdbRating")
        poster = movie_data.get("Poster")
        if name:
            self._storage.add_movie(name, year, rating, poster)
            print_colored(f"{name}, {year} has been added with a rating of {rating}.", GREEN)
            return
        print_colored("Couldn't find movie", RED)
        return

    def delete_movie(self):
        movies = self._storage.list_movies()
        print("Which movie would you like to remove?")
        name = input()
        if name in movies:
            self._storage.delete_movie(name)
            print_colored(f"{name} has been removed.", GREEN)
            return
        print_colored(f"{name} was not found in the database.", YELLOW)

    def update_movie(self):
        movies = self._storage.list_movies()
        print("Which movie would you like to update?")
        name = input()
        if name in movies:
            print(f"Enter a note for {name}:")
            note = input()
            self._storage.update_movie(name, note)
            print_colored(f"{name} has been updated with a new note: '{note}'.", GREEN)
            return
        print_colored(f"We don't seem to have {name} on the database.", YELLOW)

    def stats(self):
        movies = self._storage.list_movies()
        print("Statistics:")
        av = calc_av(movies)
        print(f"The average rating of movies in the database is {av}")
        med = calc_med(movies)
        print(f"The median rating of movies in the database is {med}")
        best, best_rate = get_best(movies)
        best_str = ', '.join(best)
        print(f"The highest rated movie(s) are: {best_str} with a rating of {best_rate:.1f}")
        worst, worst_rate = get_worst(movies)
        print(f"The lowest rated movie(s) are: {', '.join(worst)} with a rating of {worst_rate:.1f}")

    def random_movie(self):
        movies = self._storage.list_movies()
        rand = random.choice(list(movies.keys()))
        print(f"Randomly selected movie: {rand}")

    def search_movie(self):
        movies = self._storage.list_movies()
        found_movies = []
        print("Enter a part of a movie name to look for in the database:")
        search_in = input().lower()
        for movie in movies.keys():
            # Fuzz implementation
            similarity = fuzz.ratio(search_in, movie.lower())
            if similarity > 65:
                found_movies.append((movie, movies[movie]["rating"]))

        if found_movies:
            print_colored("Movies matching:", GREEN)
            for movie, m_rating in found_movies:
                print(f"{movie}, {m_rating}")
            return
        print_colored("No movies found.", YELLOW)

    def rating_list(self):
        movies = self._storage.list_movies()
        print_colored("Movies sorted by rating:", GREEN)
        sorted_movies = sorted(movies, key=lambda movie: float(movies[movie]["rating"]), reverse=True)
        for movie in sorted_movies:
            rating = movies[movie]["rating"]
            print(f"{movie}: {rating}")

    def gen_website(self):
        movies = self._storage.list_movies()
        output = ""
        if len(movies) == 0:
            output += "<h2> No movies in the database. </h2>"
            replace_in_html("index_template.html", "__TEMPLATE_MOVIE_GRID__", output)
            print_colored("Website was generated successfully.", GREEN)
            return
        for title, details in movies.items():
            output += serialize_movie(title, details)
        replace_in_html("index_template.html", "__TEMPLATE_MOVIE_GRID__", output)
        print_colored("Website was generated successfully.", GREEN)

    def run(self):
        menu_dict = {
            1: MovieApp.list_movies,
            2: MovieApp.add_movie,
            3: MovieApp.delete_movie,
            4: MovieApp.update_movie,
            5: MovieApp.stats,
            6: MovieApp.random_movie,
            7: MovieApp.search_movie,
            8: MovieApp.rating_list,
            9: MovieApp.gen_website
        }
        while True:
            choice = menu()
            if choice == 0:
                print("Goodbye!")
                break
            select_function = menu_dict.get(choice)
            if select_function:
                select_function(self)
            else:
                MovieApp.print_colored("Invalid choice", MovieApp.RED)
