from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    def on_start(self):
        pass

    @task
    def index(self):
        self.client.get("/")
        self.client.get("/about/")

    @task
    def puzzles(self):
        self.client.get("/")
        self.client.get("/puzzles/")
