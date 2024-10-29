import googlemaps
import csv
import argparse
from geopy.distance import geodesic  # To calculate distances from the center
import os

# Replace this with your actual Google API key
API_KEY = "AIzaSyDw_ghFq4Xp36M98RVQ8QVCVshh7w8tLfs"
gmaps = googlemaps.Client(key=API_KEY)

def get_city_coordinates(city_name, country_code):
    """Get the latitude and longitude for a given city."""
    geocode_result = gmaps.geocode(f"{city_name}, {country_code}")
    if geocode_result:
        location = geocode_result[0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        raise ValueError("City not found.")

def find_places_of_interest(lat, lng, radius, keyword, city_name, country_code):
    """Find places of interest within the specified radius."""
    places_result = gmaps.places_nearby(
        location=(lat, lng),
        radius=radius,
        keyword=keyword,
        language="en",
    )
    # Filter to only include places within the specified country
    places_in_country = []
    for place in places_result["results"]:
        place_details = gmaps.place(place_id=place["place_id"], language="en")["result"]
        
        # Country restriction
        if country_code in [addr['short_name'] for addr in place_details['address_components'] if 'country' in addr['types']]:
            # Distance restriction to ensure within radius
            place_location = place_details["geometry"]["location"]
            place_city = [addr['long_name'] for addr in place_details['address_components'] if 'locality' in addr['types']]
            distance = geodesic((lat, lng), (place_location["lat"], place_location["lng"])).kilometers
            if distance <= radius:
                if city_name not in place_city:
                    places_in_country.append({
                        "name": place_details["name"],
                        "address": place_details["formatted_address"],
                        #"location": (place_location["lat"], place_location["lng"]),
                        "distance": round(distance, 2)  # Display distance
                    })
                else:
                    # Append without distance for places within the city
                    places_in_country.append({
                        "name": place_details["name"],
                        "address": place_details["formatted_address"],
                        #"location": (place_location["lat"], place_location["lng"]),
                        "distance": 0  # No distance for places within the city
                    })

    return places_in_country

def save_to_csv(places, output_file="places_of_interest.csv"):
    # Save the results to a csv file
    with open(output_file, mode='w', newline='', encoding='UTF-8') as file:
        writer = csv.DictWriter(file, fieldnames=["address", "name", "distance"])
        writer.writeheader()
        for place in places:
            writer.writerow(place)
    print(f"Data saved to {output_file}")

#using Argument parser
parser = argparse.ArgumentParser(description="A python script that scrapes data from Google maps for different points of interest in a set region in a country.")
parser.add_argument('-c', '--city', required=True, help="Enter the city in English to search in")
parser.add_argument('-cd', '--country_code', required=True, help="Enter the cuntry code [BG, US] to limit the search to the set country")
parser.add_argument('-k', '--keyword', required=True, help="Enter the place of interest to search in the city and the area provided.")
parser.add_argument('-r', '--radius', type=int, required=True, help="Enter the search radius [in m, f.e. input: 1000. The search radius is equal to 1km ]")

args = parser.parse_args()

def main():

    # Get city coordinates
    try:
        city_lat, city_lng = get_city_coordinates(args.city, args.country_code)
        #print(f"Coordinates of {city_name}: {city_lat}, {city_lng}")
    except ValueError as e:
        print(e)
        return

    # Find places of interest
    places = find_places_of_interest(city_lat, city_lng, args.radius, args.keyword, args.city, args.country_code)

    # Output results
    if places:
        save_to_csv(places)
    else:
        print("No places of interest found within the specified radius.")

if __name__ == "__main__":
    main()
