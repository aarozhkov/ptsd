def test_sv_status(test_client):
    response = test_client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sv_statup(test_client):
    # TODO find out how we can check statup events work
    pass
