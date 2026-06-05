"""
API integration tests.

Run with:  pytest tests/ -v
"""
import io
import json


class TestHealth:
    def test_health_returns_200(self, client):
        res = client.get('/api/health')
        assert res.status_code == 200

    def test_health_payload(self, client):
        res = client.get('/api/health')
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['status'] == 'healthy'


class TestCreateStandup:
    BASE_PAYLOAD = {
        'author': 'Test User',
        'yesterday': 'Wrote tests.',
        'today': 'Deploying to staging.',
        'blockers': '',
    }

    def test_create_standup_success(self, client):
        res = client.post('/api/standups', data=self.BASE_PAYLOAD)
        assert res.status_code == 201
        body = res.get_json()
        assert body['success'] is True
        assert body['data']['author'] == 'Test User'

    def test_create_standup_missing_author(self, client):
        payload = {**self.BASE_PAYLOAD}
        del payload['author']
        res = client.post('/api/standups', data=payload)
        assert res.status_code == 422
        body = res.get_json()
        assert body['success'] is False
        assert 'author' in body['errors']

    def test_create_standup_missing_yesterday(self, client):
        payload = {**self.BASE_PAYLOAD}
        del payload['yesterday']
        res = client.post('/api/standups', data=payload)
        assert res.status_code == 422

    def test_create_standup_missing_today(self, client):
        payload = {**self.BASE_PAYLOAD}
        del payload['today']
        res = client.post('/api/standups', data=payload)
        assert res.status_code == 422

    def test_create_standup_with_blocker(self, client):
        payload = {**self.BASE_PAYLOAD, 'blockers': 'Waiting for API access.'}
        res = client.post('/api/standups', data=payload)
        assert res.status_code == 201
        assert res.get_json()['data']['has_blocker'] is True

    def test_create_standup_no_blocker_text_nil(self, client):
        payload = {**self.BASE_PAYLOAD, 'blockers': 'none'}
        res = client.post('/api/standups', data=payload)
        assert res.status_code == 201
        assert res.get_json()['data']['has_blocker'] is False

    def test_create_standup_file_bad_type(self, client):
        payload = {**self.BASE_PAYLOAD}
        data = {**payload, 'attachment': (io.BytesIO(b'malicious'), 'virus.exe')}
        res = client.post(
            '/api/standups',
            data=data,
            content_type='multipart/form-data',
        )
        assert res.status_code == 400

    def test_create_standup_file_valid_jpg(self, client):
        # Minimal valid JPEG header bytes
        jpeg_bytes = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            b'\xff\xd9'
        )
        payload = {
            **self.BASE_PAYLOAD,
            'attachment': (io.BytesIO(jpeg_bytes), 'screenshot.jpg'),
        }
        res = client.post(
            '/api/standups',
            data=payload,
            content_type='multipart/form-data',
        )
        assert res.status_code == 201


class TestListStandups:
    def _create(self, client, author='User A'):
        client.post('/api/standups', data={
            'author': author,
            'yesterday': 'Did things.',
            'today': 'Doing more things.',
            'blockers': '',
        })

    def test_list_returns_200(self, client):
        res = client.get('/api/standups')
        assert res.status_code == 200

    def test_list_newest_first(self, client):
        self._create(client, 'Alpha')
        self._create(client, 'Beta')
        res = client.get('/api/standups')
        items = res.get_json()['data']
        assert len(items) >= 2
        assert items[0]['author'] == 'Beta'

    def test_list_pagination(self, client):
        for i in range(5):
            self._create(client, f'User {i}')
        res = client.get('/api/standups?limit=2&offset=0')
        assert len(res.get_json()['data']) == 2


class TestStats:
    def test_stats_returns_200(self, client):
        res = client.get('/api/standups/stats')
        assert res.status_code == 200

    def test_stats_shape(self, client):
        res = client.get('/api/standups/stats')
        data = res.get_json()['data']
        assert 'total_posts' in data
        assert 'active_users_count' in data
        assert 'blocker_count' in data
        assert 'posts_per_day' in data
        assert 'blocker_per_day' in data

    def test_stats_counts_correctly(self, client):
        for _ in range(3):
            client.post('/api/standups', data={
                'author': 'Counter User',
                'yesterday': 'Yesterday.',
                'today': 'Today.',
                'blockers': '',
            })
        res = client.get('/api/standups/stats')
        data = res.get_json()['data']
        assert data['total_posts'] >= 3


class TestUnknownRoutes:
    def test_404_json(self, client):
        res = client.get('/api/does-not-exist')
        assert res.status_code == 404
        assert res.get_json()['success'] is False
