import random
from time import sleep

from bs4 import BeautifulSoup
from faker import Faker
from locust import HttpUser, between, tag, task

LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"
HOME_URL = "/"
ABOUT_URL = "/about/"
STORY_URL = "/story/"
PUZZLES_LIST_URL = "/puzzles/"
TEAMS_LIST_URL = "/teams/"

fake = Faker()


user_generator = (f"user{i}" for i in range(50))


class WebsiteUser(HttpUser):
    wait_time = between(3, 5)

    def on_start(self):
        pass

    @tag("browsing")
    @task
    def browse_site(self):
        self.client.get(HOME_URL)
        sleep(3)
        self.client.get(ABOUT_URL)
        sleep(3)
        self.client.get(STORY_URL)
        sleep(3)
        self.client.get(PUZZLES_LIST_URL)
        sleep(3)
        self.client.get(TEAMS_LIST_URL)

    def _login(self, username: str):
        response = self.client.get("/accounts/login/")
        csrf_token = response.cookies["csrftoken"]
        self.client.post(
            LOGIN_URL,
            data={
                "login": username,
                "password": "hohohomerrychristmas!",
                "csrfmiddlewaretoken": csrf_token,
            },
        )

    def _get_puzzle_urls(self, response):
        soup = BeautifulSoup(response.content, "html.parser")
        return [
            cell.find("a", href=True)["href"] for cell in soup.find_all("td", class_="puzzle-name")
        ]

    def _guess_text_factory(self) -> str:
        nb = random.randint(1, 2)
        return " ".join(fake.word() for _ in range(nb)).upper()

    @tag("solving")
    @task
    def solving_puzzles(self):
        username = next(user_generator)
        # Log into site
        self._login(username)
        response = self.client.get(PUZZLES_LIST_URL)
        puzzle_urls = self._get_puzzle_urls(response)
        random.shuffle(puzzle_urls)
        sleep(3)
        for puzzle_url in puzzle_urls:
            # Work on a random puzzle
            for _ in range(10):
                # Submit 10 guesses
                response = self.client.get(puzzle_url)
                csrf_token = response.cookies["csrftoken"]
                guess_text = self._guess_text_factory()
                self.client.post(
                    puzzle_url,
                    data={
                        "guess": guess_text,
                        "csrfmiddlewaretoken": csrf_token,
                    },
                )
                sleep(3)
            # Look at leaderboard
            self.client.get(TEAMS_LIST_URL)
            sleep(3)
            # Look at puzzle list
            self.client.get(PUZZLES_LIST_URL)
            sleep(3)
            # Look at story
            response = self.client.get(STORY_URL)
            sleep(3)
            # Logout
            csrf_token = response.cookies["csrftoken"]
            self.client.post(
                LOGOUT_URL,
                data={"csrfmiddlewaretoken": csrf_token},
            )
