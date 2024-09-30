from langchain_community.chat_models import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv
import requests
import os
import json

load_dotenv()

FLIGHT_API_KEY = os.environ.get("FLIGHT_API_KEY")

@tool
def get_airport_id(AirportName: str) -> str:
    """ A tool that allows you to get the Airport ID. Input should be a city name."""

    url = f'https://booking-com15.p.rapidapi.com/api/v1/flights/searchDestination'

    headers = {
        "X-RapidAPI-Key": FLIGHT_API_KEY,
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    querystring = {"query": AirportName}

    response = requests.get(url, headers=headers, params=querystring).json()

    return_string = ""
    for location in response.get('data', []):
        if location.get('type') == 'AIRPORT':
            return_string += f"Airport ID: {location['id']}\n"
    return return_string


@tool
def getFlightToken(input_string: str) -> str:
    """ A tool that allows you to get the token for the flight between two airports.
        The input should be in the following format:
        DepartureAirportID:ArrivalAirportID:DepartureDate:ReturnDate:NumAdults
        
        The dates should be in YYYY-MM-DD format. The year is 2024.
        Provide an empty string for the return date if it is a one way trip.
    """

    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    
    Airport1ID, Airport2ID, DepartureDate, ReturnDate, Adults = input_string.split(':')

    querystring = {
        "fromId": Airport1ID, 
        "toId": Airport2ID, 
        "departDate": DepartureDate,
        "returnDate": ReturnDate,
        "pageNo": "1",
        "adults": Adults,
        "currency_code": "USD"
        }
    
    headers = {
        "X-RapidAPI-Key": FLIGHT_API_KEY,
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring).json()

    if not response["status"]:
        return "Incorrect input provided"

    return_string = ""
    for flight in response['data'].get('flightDeals', []):
        return_string += f"Type: {flight['key']}, Token: {flight['offerToken']}\n"
    if return_string == "":
        return_string = "Couldn't find flights. Please try again."
    return return_string

@tool
def getFlightInfo(flight_token: str) -> str:
    """A function to get flight information given a flight token.
    Below if the format of the return string:

    Start location to End location:
        Leg 1:
        Departure Time: ...,
        Arrival Time: ...,
        Departure Airport: ...,
        Departure City: ...,
        Arrival Airport: ...,
        Arrival City: ...,
        Cabin Class: ...,
        Departure Terminal: ...,
        Arrival Terminal:...
    """
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/getFlightDetails"

    querystring = {"token": flight_token, "currency_code": "USD"}

    headers = {
        "X-RapidAPI-Key": FLIGHT_API_KEY,
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring).json()

    return_string = f"Trip Price: ${response['data']['priceBreakdown']['total']['units']}\n"
    for segment in response.get('data', [])['segments']:
        return_string += f"\nFrom {segment['departureAirport']['cityName']} to {segment['arrivalAirport']['cityName']}:"
        for leg in segment['legs']:
            return_string += f"""
    Departure Time: {leg['departureTime']},
    Arrival Time: {leg['arrivalTime']},
    Departure Airport: {leg['departureAirport']['name']},
    Departure City: {leg['departureAirport']['cityName']},
    Arrival Airport: {leg['arrivalAirport']['name']},
    Arrival City: {leg['arrivalAirport']['cityName']},
    Cabin Class: {leg['cabinClass']},
    Departure Terminal: {leg.get('departureTerminal', None)},
    Arrival Terminal: {leg.get('arrivalTerminal', None)}
"""
    return return_string

if __name__ == "__main__":
    from langchain.agents import initialize_agent

    tools = [get_airport_id, getFlightToken, getFlightInfo]

    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0,
        model_name="gpt-3.5-turbo"
    )

    zero_shot_agent = initialize_agent(
        agent="zero-shot-react-description",
        tools=tools,
        llm=llm,
        verbose=True,
        max_iterations=200
    )

    zero_shot_agent("""I live in New York. I want to go to Mexico City for 14 days. I plan on leaving on May 1.
                    Can you find me the best flights? I want to know all the information there is to know about the flights you choose.
                    I want the flight itinerary in list form.
                    The list should have a sublist with details about any layovers.
                    You must give me information about my flights!""")
