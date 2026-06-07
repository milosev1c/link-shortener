import pytest


@pytest.mark.asyncio
async def test_redirect_known_id_returns_307(client):
    shorten = await client.post(
        "/links/shorten",
        json={"long_url": "https://www.example.org"},
    )
    short_url = shorten.json()["short_url"]
    short_id = short_url.rsplit("/", 1)[-1]

    response = await client.get(f"/u/{short_id}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://www.example.org/"


@pytest.mark.asyncio
async def test_redirect_unknown_id_returns_404(client):
    response = await client.get("/u/doesnotexist", follow_redirects=False)

    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}


@pytest.mark.asyncio
async def test_redirect_invalid_id_returns_404(client):
    response = await client.get("/u/bad id!", follow_redirects=False)

    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}


@pytest.mark.asyncio
async def test_shorten_then_redirect_round_trip(client):
    shorten = await client.post(
        "/links/shorten",
        json={"long_url": "https://www.example.org/path"},
    )

    assert shorten.status_code == 201
    short_id = shorten.json()["short_url"].rsplit("/", 1)[-1]

    redirect = await client.get(f"/u/{short_id}", follow_redirects=False)

    assert redirect.status_code == 307
    assert redirect.headers["location"] == "https://www.example.org/path"
