from unittest.mock import Mock, MagicMock
import pandas as pd
from waf_data.waf_data_getter import WAFDataGetter
import requests
import pytest

class TestWAFDataGetter():
    def test_get_waf_data_success(self):
        mock_http_client = Mock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "1", "rule": "SQLi", "action": "block"},
            {"id": "2", "rule": "XSS", "action": "alert"}
        ]
        mock_http_client.get.return_value = mock_response

        waf_getter = WAFDataGetter(
            data_location="http://test.com/data",
            secret="test_secret",
            http_client=mock_http_client
        )

        waf_data = waf_getter.get_waf_data()

        mock_http_client.get.assert_called_once_with(
            "http://test.com/data",
            headers={"Authorization": "Bearer test_secret"}
        )
        assert type(waf_data) == pd.DataFrame
        assert len(waf_data) == 2


    def test_get_waf_data_failure(self):
        # Create a mock http_client for a failure scenario
        mock_http_client = Mock()

        # Configure the mock's 'get' method to raise an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_http_client.get.return_value = mock_response

        waf_getter = WAFDataGetter(
            data_location="http://test.com/data",
            secret="test_secret",
            http_client=mock_http_client
        )

        with pytest.raises(requests.exceptions.HTTPError):
            waf_getter.get_waf_data()

        mock_http_client.get.assert_called_once()
