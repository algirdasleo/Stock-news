# Stock News: Stock symbols & News Notifications

Stock-news is a Python program that lets user request emails about the most active stocks and top financial news. It retrieves data from the **Alpaca API** and **News API** and formats it for email delivery.

## Features
- Retrieve Top 10 most active stocks by volume/trades.
- Fetch the latest stock related news.
- Send emails with the stock data/news to the user.
- Email validation and SMTP integration for email sending.

## Requirements
- Python 3.6+
- Install dependencies:
  ```bash
  pip install -r requirements.txt

## Setup


1. Create a `.env` file in the root of the project directory and add your API keys:

    ```
    ALPACA_API_KEY=your_alpaca_api_key
    ALPACA_API_SECRET=your_alpaca_api_secret
    NEWS_API_KEY=your_news_api_key
    EMAIL_ADDRESS=your_email_address
    EMAIL_PASSWORD=your_email_password
    ```

2. Install the required dependencies:

    ```bash
    pip install requests email-validator python-dotenv
    ```

## Usage

Run the program by providing your email and API choice (either "news" or "stocks"):

```bash
python3 news.py <your_email_address> <api_choice>
```

## Example:

```bash
python3 news.py user@example.com stocks
```
### Options for `<api_choice>`:
- `stocks` - Retrieves the most active stocks by volume or trades.
- `news` - Retrieves the latest stock-related news.
