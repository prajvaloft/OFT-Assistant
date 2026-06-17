import requests
import webbrowser


def open_maps():

    data = requests.get(
        "https://ipinfo.io/json",
        timeout=5
    ).json()

    loc = data.get("loc")

    if not loc:
        return "Unable to get location."

    lat, lon = loc.split(",")

    url = (
        f"https://www.google.com/maps/search/"
        f"?api=1&query={lat},{lon}"
    )

    webbrowser.open(url)

    return "Opened your location in Google Maps."