from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from models import StationModel


def get_station_location(station: StationModel):
    geolocator = Nominatim(user_agent="city_locator")
    try:
        search_name = station.city
        location = geolocator.geocode(search_name)

        if location:
            station_lat = location.latitude
            station_lon = location.longitude
            return station_lat, station_lon
        else:
            return "City Not Found"

    except GeocoderTimedOut:
        return "Error, timeout."