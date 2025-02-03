import pytest
from unittest.mock import patch, MagicMock
from stocknews import validate_email_address, get_news, format_news, format_stocks, get_stocks


def test_validate_email_address_valid():
    assert validate_email_address("example@gmail.com") == True
    assert validate_email_address("user123@yahoo.com") == True
    assert validate_email_address("contact@outlook.com") == True
    assert validate_email_address("name.username@icloud.com") == True
    assert validate_email_address("test.email@domain.co.uk") == True
    assert validate_email_address("name!#@email.com") == True

def test_validate_email_address_invalid():
    assert validate_email_address("") == False
    assert validate_email_address("@gmail.com") == False
    assert validate_email_address("username@") == False
    assert validate_email_address("name@domain") == False

def test_format_stocks():
    stocks_json = {
        "most_actives": [
            {"symbol": "AAPL", "trade_count": 500000, "volume": 1000000},
            {"symbol": "GOOG", "trade_count": 400000, "volume": 900000}
        ]
    }
    rank_choice = "volume"
    email_title, email_description = format_stocks(rank_choice, stocks_json)
    assert email_title == "Top 10 Stocks By Volume"
    assert "AAPL" in email_description
    assert "500,000" in email_description
    assert "1,000,000" in email_description
    assert "GOOG" in email_description
    assert "400,000" in email_description

def test_format_news():
    news_json = {
        "data": [
            {"title": "Stock News 1", "description": "Description 1", "url": "http://example1.com"},
            {"title": "Stock News 2", "description": "Description 2", "url": "http://example2.com"}
        ]
    }
    email_title, email_description = format_news(news_json)
    assert email_title == "Top 3 Stock Market News"
    assert "Story 1 ----" in email_description
    assert "Title: Stock News 1" in email_description
    assert "Description: Description 1" in email_description
    assert "Url: http://example1.com" in email_description
    assert "Story 2 ----" in email_description
    assert "Title: Stock News 2" in email_description

# Mock successful response from The News API
@patch("requests.get")
def test_get_news_valid(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "data": [
            {"title": "Stock News 1", "description": "Description 1", "url": "http://example1.com"},
            {"title": "Stock News 2", "description": "Description 2", "url": "http://example2.com"},
        ]
    }
    
    result = get_news()
    assert result is not None
    assert "data" in result
    assert len(result["data"]) == 2
    assert result["data"][0]["title"] == "Stock News 1"
    assert result["data"][0]["description"] == "Description 1"
    assert result["data"][0]["url"] == "http://example1.com"

# Mock unsuccessful response from The News API
@patch('requests.get')
def test_get_news_invalid(mock_get):
    mock_get.return_value.status_code = 500  
    mock_get.return_value.json.return_value = {"error": {"message": "Internal Server Error"}}
    
    result = get_news() 
    
    assert result is None

# Mock successful response from Alpaca API
@patch('requests.get')
def test_get_stocks_valid(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "most_actives": [
            {"symbol": "AAPL", "trade_count": 15000, "volume": 500000},
            {"symbol": "TSLA", "trade_count": 12000, "volume": 450000},
            {"symbol": "GOOG", "trade_count": 10000, "volume": 400000}
        ]
    }
    
    rank_choice = 'volume'
    result = get_stocks(rank_choice)

    assert result is not None
    assert len(result["most_actives"]) == 3  # We expect 3 stocks in the list
    assert result["most_actives"][0]["symbol"] == "AAPL"
    assert result["most_actives"][0]["trade_count"] == 15000
    assert result["most_actives"][0]["volume"] == 500000

# Mock unsuccessful response from Alpaca API
@patch('requests.get')
def test_get_stocks_invalid(mock_get):
    mock_get.return_value.status_code = 500
    mock_get.return_value.json.return_value = {"message": "Internal Server Error"}
    
    rank_choice = 'volume'
    result = get_stocks(rank_choice)

    assert result is None  

