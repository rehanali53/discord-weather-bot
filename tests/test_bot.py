import pytest
from bot.weather import get_current_weather
from bot.api_integration import MistralAIHandler

def test_weather_mapping(monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {"weather": [{"main": "Rain"}]}
            status_code = 200
        return MockResponse()
    
    monkeypatch.setattr("requests.get", mock_get)
    assert get_current_weather() == "rainy"

def test_mistral_handler():
    handler = MistralAIHandler()
    assert handler.api_key is not None
