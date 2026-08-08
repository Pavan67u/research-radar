def test_list_search_filter_and_pagination(client):
    response = client.get('/papers', params={'q':'models','topic':'Machine','page':1,'page_size':2})
    assert response.status_code == 200
    body = response.json(); assert body['total'] == 4; assert len(body['items']) == 2; assert body['pages'] == 2
    assert client.get('/papers', params={'author':'Grace'}).json()['total'] == 3
    assert client.get('/papers', params={'year':2024}).json()['total'] == 1

def test_detail_found_and_404(client):
    assert client.get('/papers/1').status_code == 200
    assert client.get('/papers/999').status_code == 404

def test_similar_found_and_404(client):
    response = client.get('/papers/1/similar')
    assert response.status_code == 200; assert len(response.json()) == 5
    assert client.get('/papers/999/similar').status_code == 404

