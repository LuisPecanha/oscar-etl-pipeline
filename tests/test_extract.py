import pandas as pd
from unittest.mock import patch, Mock
from src.etl.extract import extract_awards_data

@patch("etl.extract.SESSION.get")
def test_extract_awards_data_success(mock_get, mock_awards_api_response):
    """
    Test that, when the awards‐API returns a well‐formed JSON payload, 
    extract_awards_data() returns a non‐empty DataFrame with exactly the 
    expected columns and correct sample content.
    """

    # Arrange
    # mock_response simulates a 200 OK + valid JSON body from the API
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = mock_awards_api_response
    mock_get.return_value = mock_response

    # Act
    df = extract_awards_data()

    # Assert
    # Sanity Check
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Structure Check
    assert set(df.columns) == {"film", "year", "wikipedia_url", "oscar_winner", "detail_url"}
    # Contenct check
    assert df.iloc[0]["film"] == "Titanic"