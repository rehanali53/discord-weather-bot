import openai
from openai import OpenAI
import json
from dotenv import load_dotenv
from .hsl import get_optimal_route
from typing import List, Dict, Any
from openai.types.chat import ChatCompletionToolParam
import os

load_dotenv()

# Initialize the client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_openai_response(prompt: str):
    tools: List[ChatCompletionToolParam] = [
        {
            "type": "function",
            "function": {
                "name": "get_weather_based_route",
                "description": "Get optimal transportation route based on current weather conditions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Starting location, e.g. Helsinki Central Station"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination location, e.g. Helsinki Airport"
                        },
                        "weather_condition": {
                            "type": "string",
                            "enum": ["sunny", "rainy", "snowy", "windy", "foggy"],
                            "description": "Current weather condition"
                        }
                    },
                    "required": ["origin", "destination", "weather_condition"]
                }
            }
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
        tool_choice="auto"
    )
    
    return response

def handle_function_call(function_name, arguments):
    if function_name == "get_weather_based_route":
        return get_optimal_route(**arguments)
    return {"error": "Function not implemented"}