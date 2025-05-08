import pytest
from src.etl.transform import parse_budget_value


@pytest.fixture
def conversion_rates():
    """Standard currency conversion rates (USD per unit of foreign currency)."""
    return {
        "$": 1.0,
        "us$": 1.0,
        "€": 1.08,
        "£": 1.25,
        "₤": 0.000558,
    }


def test_parse_budget_value_usd_million(conversion_rates):
    """
    Given a budget string in USD with unit “million”,
    parse_budget_value() should return the correct integer amount.
    """

    # Arrange
    input_value = "$10 million"
    # Act
    result = parse_budget_value(input_value, conversion_rates)
    # Assert
    assert result == 10_000_000, f"Expected 10_000_000, got {result}"


def test_parse_budget_value_euro_billion(conversion_rates):
    """
    Given a budget string in EUR with unit “billion”,
    parse_budget_value() should apply the unit multiplier
    then convert at the provided rate.
    """

    # Arrange
    input_value = "€2 billion"
    # Act
    result = parse_budget_value(input_value, conversion_rates)
    # Assert
    assert result == int(
        2_000_000_000 * 1.08
    ), f"Expected {int(2_000_000_000 * conversion_rates['€'])}, got {result}"
