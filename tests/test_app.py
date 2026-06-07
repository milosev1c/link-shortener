import link_shortener.api.routes as routes_module


async def test_app_title(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "link-shortener"


def test_routes_module_importable():
    assert hasattr(routes_module, "router")
