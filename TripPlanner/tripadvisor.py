from langchain_community.chat_models import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv
import requests
import os

load_dotenv()

TRIPADVISOR_API_KEY = os.environ.get("TRIPADVISOR_API_KEY")

@tool
def get_nearby_attraction(latLong: str) -> str:
    """A tool that allows you to get attractions close to a given lattitude and longitude pair. The input should just be a pair of floats that looks like this: 51.5074, -0.1278. Do not add any other text."""

    url = f'https://api.content.tripadvisor.com/api/v1/location/nearby_search'

    headers = {"accept": "application/json"}

    response = requests.get(url, params={"latLong": latLong, "key": TRIPADVISOR_API_KEY, "category":"attractions"}, headers=headers).json()
 
    return_string = ""
    for location in response.get('data', []):
        return_string += f"Location ID: {location['location_id']}, Name: {location['name']}\n"

    if return_string == "":
        return_string = "Could not find the information requested"
    return return_string

@tool
def get_nearby_hotel(latLong: str) -> str:
    """A tool that allows you to get hotels close to a given lattitude and longitude pair. The input should just be a pair of floats that looks like this: 51.5074, -0.1278. Do not add any other text."""

    url = f'https://api.content.tripadvisor.com/api/v1/location/nearby_search'

    headers = {"accept": "application/json"}

    response = requests.get(url, params={"latLong": latLong, "key": TRIPADVISOR_API_KEY, "category":"hotels"}, headers=headers).json()
 
    return_string = ""
    for location in response.get('data', []):
        return_string += f"Location ID: {location['location_id']}, Name: {location['name']}\n"

    if return_string == "":
        return_string = "Could not find the information requested"
    return return_string

@tool
def get_nearby_restaurants(latLong: str) -> str:
    """A tool that allows you to get restaurants close to a given lattitude and longitude pair. The input should just be a pair of floats that looks like this: 51.5074, -0.1278. Do not add any other text."""

    url = f'https://api.content.tripadvisor.com/api/v1/location/nearby_search'

    headers = {"accept": "application/json"}

    response = requests.get(url, params={"latLong": latLong, "key": TRIPADVISOR_API_KEY, "category":"restaurants"}, headers=headers).json()
 
    return_string = ""
    for location in response.get('data', []):
        return_string += f"Location ID: {location['location_id']}, Name: {location['name']}\n"

    if return_string == "":
        return_string = "Could not find the information requested"
    return return_string

@tool
def get_location_info(location_id: str) -> str:
    """A tool that returns information about a location. The input should be an 8 digit numeric location id without extra information."""
    url = f'https://api.content.tripadvisor.com/api/v1/location/{location_id}/details'

    headers = {"accept": "application/json"}

    response = requests.get(url, params={"key": TRIPADVISOR_API_KEY}, headers=headers).json()
    return f"""
Name: {response.get("name", None)}
Description: {response.get("description", None)}
Phone: {response.get("phone", None)}
Website: {response.get("website", None)}
Rating: {response.get("rating", None)}
Price Level: {response.get("price_level", None)}
Hours:
Features: {response.get("features", None)}
Amenities: {response.get("amenities", None)}
"""

@tool 
def get_location_reviews(location_id: str) -> str:
    """A tool that returns reviews about one given location_id. The input should be an 8 digit numeric location id without extra information."""
    url = f'https://api.content.tripadvisor.com/api/v1/location/{location_id}/reviews'

    headers = {"accept": "application/json"}

    response = requests.get(url, params={"key": TRIPADVISOR_API_KEY}, headers=headers).json()
    return_string = ""

    for review in response.get('data', []):
        return_string += f"Location ID: {review['location_id']}, Rating: {review['rating']}, Title: {review['title']}, Review: {review['text']}\n"

    if return_string == "":
        return_string = "Could not find the information requested"

    return return_string

@tool
def get_location_photos(location_id: str) -> str:
    """A tool that returns photos about one given location_id. The input should be an 8 digit location id number without extra information."""
    url = f'https://api.content.tripadvisor.com/api/v1/location/{location_id}/photos'

    headers = {"accept": "application/json"}

    response = requests.get(url, params={"key": TRIPADVISOR_API_KEY}, headers=headers).json()
    return_string = ""

    for photo in response.get('data', []):
        return_string += f"Location ID: {photo['id']}, Image: {photo['images']}, Caption: {photo['caption']}, Blessed: {photo['is_blessed']}\n"

    if return_string == "":
        return_string = "Could not find the information requested"
    return return_string


if __name__ == "__main__":
    from langchain.agents import initialize_agent

    tools = [get_nearby_attraction, get_location_info, get_nearby_hotel, get_nearby_restaurants, get_location_reviews, get_location_photos]

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
        max_iterations=40
    )

    location = "Seattle"
    # zero_shot_agent(f"""Find me restaurants near {location}. Sort the restaurants by their rating. 
    #                 For the three highest rated restaurants, give me three reviews.
    #                 For each restaurant, sort the reviews in your answer by rating. Give the two highest rating reviews and the lowest rating review.
    #                 For each review, your answer must include the name of the restaurant, the rating given by the review, the title of the review, and the text of the review in list format.
    #                 """)
    zero_shot_agent(f"""Find me one restaurant near {location}. Get one photo of this restaurant.
                    For this photo, output a response in list format containing the location name, a link to the photo, the caption, and the blessed status of the photo.""")
