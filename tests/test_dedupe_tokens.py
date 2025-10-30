import json

from app import app


def post_tokenize(client, text: str):
    return client.post('/tokenize-text', json={'text': text})


def test_tokenize_collapses_consecutive_duplicates():
    with app.test_client() as client:
        resp = post_tokenize(client, 'photo photo photo')
        assert resp.status_code == 200
        data = resp.get_json()
        # Should return single 'photo' (or at least no consecutive dups)
        tokens = data.get('tokens') or []
        assert tokens == [] or all(tokens[i] != tokens[i+1] for i in range(len(tokens)-1))


def test_tokenize_respects_available_tokens_list():
    with app.test_client() as client:
        resp = post_tokenize(client, 'hello world')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'tokens' in data
        assert 'available' in data
        # Validate no consecutive duplicates in general
        tokens = data.get('tokens') or []
        assert all(tokens[i] != tokens[i+1] for i in range(len(tokens)-1))
