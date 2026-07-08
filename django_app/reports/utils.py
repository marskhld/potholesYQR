import requests

def geocode_address(address):
    """
    Geocode an address using the OpenStreetMap Nominatim API.

    Args:
        address (str): The address to geocode.

    Returns:
        dict: A dictionary containing the latitude and longitude of the address.
              Returns None if the address could not be geocoded.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'potholesYQR/1.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            return {
                'latitude': data[0]['lat'],
                'longitude': data[0]['lon']
            }
        else:
            return None
    except requests.RequestException as e:
        print(f"Error geocoding address: {e}")
        return None