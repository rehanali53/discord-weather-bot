def get_optimal_route(origin, destination, weather_condition):
    # Mock HSL API responses based on weather
    routes = {
        "sunny": {
            "recommendation": "Take a bike or walk if distance is short",
            "routes": [
                {"type": "bike", "duration": "15 min", "details": "City Bike available at station"},
                {"type": "walk", "duration": "25 min", "details": "Pleasant weather for walking"}
            ]
        },
        "rainy": {
            "recommendation": "Public transport is recommended",
            "routes": [
                {"type": "tram", "duration": "12 min", "details": "Tram 4 to Mannerheimintie"},
                {"type": "bus", "duration": "18 min", "details": "Bus 55 to Airport"}
            ]
        },
        "snowy": {
            "recommendation": "Use metro or trams which are more reliable in snow",
            "routes": [
                {"type": "metro", "duration": "10 min", "details": "M1 to Helsinki Central"},
                {"type": "tram", "duration": "15 min", "details": "Tram 6 to Hietalahti"}
            ]
        }
    }
    
    default_response = {
        "recommendation": "Multiple options available",
        "routes": [
            {"type": "bus", "duration": "20 min", "details": "Bus 30 to city center"},
            {"type": "metro", "duration": "15 min", "details": "M2 to Tapiola"}
        ]
    }
    
    return routes.get(weather_condition, default_response)