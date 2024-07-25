import pytest

from huntsite.content.factories import AboutEntryFactory

pytestmark = pytest.mark.django_db


def test_about_page(client):
    AboutEntryFactory(
        title="But do you recall the most famous reindeer of all?",
        content="Rudolph the red-nosed reindeer had a very shiny nose.",
    )
    AboutEntryFactory(
        title="Won't you guide my sleigh tonight?",
        content="Rudolph the Red-Nosed Reindeer, you'll go down in history.",
    )

    response = client.get("/about/")
    assert response.status_code == 200
    assert b"But do you recall" in response.content
    assert b"had a very shiny nose" in response.content
    assert b"guide my sleigh tonight" in response.content
    assert b"go down in history" in response.content


def test_story_page(client):
    pass
