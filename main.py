import sys
import requests
from email_validator import validate_email, EmailNotValidError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load sensitive information
load_dotenv()

alpaca_key = os.getenv("ALPACA_API_KEY")
alpaca_secret = os.getenv("ALPACA_API_SECRET")
alpaca_url = "https://data.alpaca.markets/v1beta1/screener/stocks/most-actives"
news_api_key = os.getenv("NEWS_API_KEY")
news_url = f"https://api.thenewsapi.com/v1/news/top?api_token={news_api_key}&locale=us&limit=5"
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")

def main():
    # Check if user provided the required email and API choice
    if len(sys.argv) != 3:
        sys.exit("Please provide required parameters: python3 news.py <Email Address> <API Name>")
    
    user_email = sys.argv[1]
    api_choice = sys.argv[2].lower()
    
    # Validate email using email_validator library
    if not validate_email_address(user_email):
        sys.exit("The provided email address is invalid. Please correct it and try again.")
    
    if api_choice not in ["news", "stocks"]:
        sys.exit("Please provide a valid API name, f.e. News, Stocks. Please correct it and try again.")
    
    # Inform user about successful selection and ask for additional clarifications
    if api_choice == "stocks":
        print("Successfully selected API Option for Most Active Stocks by Volume or Trade Count.")
        while True:
            # Enable user to select sorting type
            rank_choice = input("Sort by Volume Or Trades?: ").strip().lower()
            if rank_choice not in ["volume", "trades"]:
                print("Invalid choice selected! Pick either volume or trades.")
                continue
            break
    else:
        print("Successfully selected API Option for news delivery! Continuing.")
    
    if api_choice == "news":
        received_news_json = get_news()
        if not received_news_json:
            sys.exit("Error while fetching rows. Exiting.")
            
        email_title, email_description = format_news(received_news_json)
        
    elif api_choice == "stocks":
        received_stocks_json = get_stocks(rank_choice)
        if not received_stocks_json:
            sys.exit("Error while fetching stocks. Exiting.")
            
        email_title, email_description = format_stocks(rank_choice, received_stocks_json)
        
    # Send information to user email
    if send_email(user_email, email_title, email_description):
        print(f"Email to {user_email} sent successfully!")
    else:
        print("Failed to send email. Exiting.")    


def validate_email_address(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError as e:
        print(f"Invalid Email: {e}")
        return False

def get_news():
    # Pass required parameters according to The News API docs:
    # https://www.thenewsapi.com/documentation#top-stories
    params = {
        "api_token": news_api_key,
        "locale": "us",
        "limit": 3,
        "search": "stocks"
    }
    try:
        response = requests.get(news_url, params=params)
    except requests.exceptions.RequestException as e:
        print(f"Request Exception Occured: {e}")
        return None
    
    # Use try/except in case response is received invalid
    try:
        response_json = response.json()
    except ValueError as e:
        print(f"Received invalid JSON Error from The News API: {e}")
        return None
    
    # Check status code to provide more detail about the issue, inform the user
    if response.status_code != 200:
        if response_json.get("error"):
            print(f"The News API Error: {response_json['error']['message']}")
        else:
            print(f"Received invalid status code from The News API: {response.status_code}")
        return None
    else:
        print("Successfully fetched News Data!")
        return response_json

def format_news(news_json):
    # Extracts data from json to list of tuples
    extracted_news = [(news["title"], news["description"], news["url"]) for news in news_json["data"]]
    
    email_title = "Top 3 Stock Market News"
    email_description = "Here are the stock market news you requested:\n"
    
    for i, news in enumerate(extracted_news):
        email_description += f"\n Story {i + 1} ----"
        email_description += f"\n Title: {news[0]}"
        email_description += f"\n Description: {news[1]}"
        email_description += f"\n Url: {news[2]}\n"

    return email_title, email_description
    
def get_stocks(rank_choice):
    # Pass required parameters and headers according to Alpaca Markets documentation:
    # https://docs.alpaca.markets/reference/mostactives-1
    params = {
        "by": rank_choice,
        "top": 10
    }
    
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": alpaca_key,
        "APCA-API-SECRET-KEY": alpaca_secret
    }
    
    try:
        response = requests.get(alpaca_url, params=params, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"Request Exception Occured: {e}")
        return None
    
    try:
        response_json = response.json()
    except ValueError as e:
        print(f"Received invalid JSON Error from Alpaca API: {e}")
        return None
        
    if response.status_code != 200:
        error_message = response_json.get("message")
        if error_message:
            print(f"Alpaca API Error: {error_message}")
        else:
            print(f"Error: Received invalid request status code: {response.status_code}")
        return None
    else:
        print("Successfully fetched Stocks Data!")
        return response_json

def format_stocks(rank_choice, stocks_json):
    # Extracts data from json to list of tuples
    extracted_stocks = [(stock["symbol"], stock["trade_count"], stock["volume"]) for stock in stocks_json["most_actives"]]

    if rank_choice == "trades":
        rank_choice = "Trade Count"
        
    email_title = f"Top 10 Stocks By {rank_choice.title()}"
    email_description = f"Here are the stocks you requested, ranked by {rank_choice.title()}:\n\n"
    
    for stock in extracted_stocks:
        email_description += f"• {stock[0]} - Trade Count: {stock[1]:,}, Volume: {stock[2]:,}\n"
    
    return email_title, email_description

def send_email(user_email, email_title, email_description):
    # Creates and sends the email using SMTP
    msg = MIMEMultipart()
    msg["Subject"] = email_title
    msg["From"] = email_address
    msg["To"] = user_email
    msg.attach(MIMEText(email_description, "plain"))
    
    smtp_server = "smtp.gmail.com"
    # Port 465 is used with "SMTP over SSL"
    smtp_port = 465
    
    try:
        # Establishes connection with SMTP Gmail server using SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            # Logs in with the set credentials
            server.login(email_address, email_password)
            # Sends email to user provided email
            server.sendmail(email_password, user_email, msg.as_string())
            # Returns successful bool true
            return True
    except Exception as e:
        # If any error is encountered, user is informed about the issue
        print(f"Encountered an error while sending email: {e}")
        # Returns unsuccessful bool false
        return False

if __name__ == "__main__":
    main()
