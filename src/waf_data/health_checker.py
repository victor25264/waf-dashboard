import requests

class HealthChecker:
    def __init__(self, url, token, http_client=requests) -> None:
        self.url = url
        self.token = token
        self.http_client = http_client

    def is_service_healthy(self):
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.http_client.get(self.url, headers=headers, timeout=5)
            return response.status_code == 200
        except self.http_client.RequestException:
            return False