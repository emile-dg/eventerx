
def test_tc01(client):
    rv = client.get("/")
    assert b"You need to login to get access to that page" in rv.data


# def test_tc02(client):
#     pass


# def test_tc02(client):
#     pass