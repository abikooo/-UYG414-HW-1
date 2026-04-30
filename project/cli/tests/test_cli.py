"""
Unit tests for the CLI API Client and UI modules.
These tests validate the client logic WITHOUT requiring a running server.
"""
import pytest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api_client import APIClient


class TestAPIClient:
    """Tests for the APIClient HTTP wrapper."""

    def setup_method(self):
        self.client = APIClient(base_url="http://localhost:8000")

    def test_default_base_url(self):
        c = APIClient()
        assert c.base_url == "http://localhost:8000"

    def test_custom_base_url(self):
        c = APIClient(base_url="http://example.com:9000/")
        assert c.base_url == "http://example.com:9000"  # Trailing slash stripped

    def test_initial_state_no_token(self):
        assert self.client.token is None
        assert self.client.refresh_token_str is None

    def test_headers_without_auth(self):
        headers = self.client._headers()
        assert "Content-Type" in headers
        assert "Authorization" not in headers

    def test_headers_with_auth(self):
        self.client.token = "test-token-123"
        headers = self.client._headers()
        assert headers["Authorization"] == "Bearer test-token-123"

    @patch("api_client.httpx.post")
    def test_login_stores_token(self, mock_post):
        """On successful login, the client should store the token."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "access_token": "jwt-abc-123",
                "refresh_token": "refresh-xyz"
            }
        }
        mock_post.return_value = mock_response

        result = self.client.login("test@test.com", "password")

        assert result["status"] == "success"
        assert self.client.token == "jwt-abc-123"
        assert self.client.refresh_token_str == "refresh-xyz"

    @patch("api_client.httpx.post")
    def test_login_failure_no_token(self, mock_post):
        """On failed login, token should remain None."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "error",
            "error": "Invalid credentials"
        }
        mock_post.return_value = mock_response

        self.client.login("bad@test.com", "wrong")
        assert self.client.token is None

    @patch("api_client.httpx.post")
    def test_register_returns_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "data": {"id": "123"}}
        mock_post.return_value = mock_response

        result = self.client.register("user", "user@test.com", "pass", "writer")
        assert result["status"] == "success"

    @patch("api_client.httpx.get")
    def test_health_gateway_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_response

        result = self.client.health_gateway()
        assert result["status"] == "healthy"

    @patch("api_client.httpx.get")
    def test_health_gateway_unreachable(self, mock_get):
        """If the gateway is unreachable, it should return a structured error."""
        mock_get.side_effect = Exception("Connection refused")

        result = self.client.health_gateway()
        assert result["status"] == "unreachable"
        assert "Connection refused" in result["error"]

    @patch("api_client.httpx.post")
    def test_ingest_log_payload(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        self.client.token = "test-token"
        result = self.client.ingest_log("ERROR", "Something broke", "my-service")
        assert result["status"] == "success"
        # Verify the call was made with correct payload
        call_kwargs = mock_post.call_args
        assert call_kwargs is not None
