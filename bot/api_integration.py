import os
import json
import requests
from .hsl import get_optimal_route
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

class MistralAIHandler:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_chat_completion(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        """Get chat completion from Mistral AI"""
        payload: Dict[str, Any] = {
            "model": "mistral-small-latest",
            "messages": messages,
            "temperature": 0.7
        }

        if tools:
            payload["tools"] = tools

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=10  # Add timeout to prevent hanging
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling Mistral API: {e}")
            return None

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Mistral AI tool calls"""
        if tool_name == "get_weather_based_route":
            
            try:
                return get_optimal_route(**arguments)
            except Exception as e:
                print(f"Error in get_optimal_route: {e}")
                return {"error": str(e)}
        return {"error": f"Tool {tool_name} not implemented"}

def get_mistral_response(prompt: str) -> Dict[str, Any]:
    """Get response from Mistral AI with function calling capability"""
    tools: List[Dict[str, Any]] = [
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

    handler = MistralAIHandler()
    messages: List[Dict[str, str]] = [{"role": "user", "content": prompt}]
    
    response = handler.get_chat_completion(messages, tools)
    if not response:
        return {"choices": []}  # Return empty response instead of None

    # Process tool calls if any
    if response.get("choices") and len(response["choices"]) > 0:
        choice = response["choices"][0]
        message = choice.get("message", {})
        if "tool_calls" in message and message["tool_calls"]:
            tool_call = message["tool_calls"][0]  # Assuming first tool call
            function_name = tool_call["function"]["name"]
            try:
                arguments = json.loads(tool_call["function"]["arguments"])
                return {
                    "choices": [{
                        "message": {
                            "content": None,
                            "function_call": {
                                "name": function_name,
                                "arguments": arguments
                            }
                        }
                    }]
                }
            except json.JSONDecodeError as e:
                print(f"Error parsing tool arguments: {e}")

    return response or {"choices": []}  # Ensure we always return a dict

def handle_function_call(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle function calls from either Mistral or OpenAI"""
    handler = MistralAIHandler()
    return handler.handle_tool_call(function_name, arguments)

# For backward compatibility with existing code
get_openai_response = get_mistral_response