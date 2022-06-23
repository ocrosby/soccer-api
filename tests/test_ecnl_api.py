def test_get_clubs(app, client):
    del app
    res = client.get("/api/ecnl/clubs")
    assert res.status_code == 200
    data = res.json
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Item 1"
    assert len(data[0]["details"]) == 2
    