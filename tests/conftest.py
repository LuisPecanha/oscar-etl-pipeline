import pytest


@pytest.fixture
def mock_awards_api_response():
    return {
        "results": [
            {
                "year": 1997,
                "films": [
                    {
                        "Film": "Titanic",
                        "Winner": True,
                        "Wiki URL": "http://example.com/titanic",
                        "Detail URL": "http://example.com/details/titanic",
                    }
                ],
            }
        ]
    }
