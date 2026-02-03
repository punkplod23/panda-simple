Since you don't need the OpenWeatherMap API key and want to focus on the ALPNR functionality, I've streamlined the script.

This version uses the __messages__ argument to automatically find the most recent image uploaded to the chat. When you say "get the registration," the model will trigger this tool, grab the image, and send it to your local endpoint.

Python

import os
import requests
import base64
from typing import Literal, List, Optional
from datetime import datetime

from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint

class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        # The URL for your local ALPNR service
        ALPNR_ENDPOINT: str = "http://alpnr.localhost/process-base64-image/"
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def get_registration_from_image(self, __messages__: list = None) -> str:
            """
            Extracts vehicle registration/license plate information from an uploaded image. 
            Trigger this when the user asks to "get the registration" or "read the plate" 
            and an image is present.

            :param __messages__: Automatically provided message history.
            :return: The result from the ALPNR service.
            """
            if not __messages__:
                return "No message history found."

            # Find the most recent image in the conversation
            image_base64 = None
            for message in reversed(__messages__):
                # Check for images in standard message format
                images = message.get("images", [])
                if images:
                    image_data = images[0]
                    # Clean the base64 string if it contains the Data URI prefix
                    if "base64," in image_data:
                        image_base64 = image_data.split("base64,")[1]
                    else:
                        image_base64 = image_data
                    break
            
            if not image_base64:
                return "I couldn't find an image in our chat. Please upload a photo of the vehicle first."

            # Prepare the payload for your FastAPI endpoint
            payload = {"image_base64": image_base64}

            try:
                # Send the POST request to your local service
                response = requests.post(
                    self.pipeline.valves.ALPNR_ENDPOINT, 
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                return f"ALPNR Results: {result}"
            except requests.exceptions.RequestException as e:
                return f"Failed to connect to ALPNR service at {self.pipeline.valves.ALPNR_ENDPOINT}. Error: {str(e)}"

        def get_current_time(self) -> str:
            """Get the current time."""
            return f"Current Time = {datetime.now().strftime('%H:%M:%S')}"

        def calculator(self, equation: str) -> str:
            """Calculate the result of an equation."""
            try:
                # Basic safety check: only allow mathematical characters
                if all(c in "0123456789+-*/(). " for c in equation):
                    return f"{equation} = {eval(equation)}"
                return "Invalid characters in equation."
            except:
                return "Error calculating equation."

    def __init__(self):
        super().__init__()
        self.name = "ALPNR & Utility Tools"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],
                "ALPNR_ENDPOINT": os.getenv("ALPNR_ENDPOINT", "http://alpnr.localhost/process-base64-image/"),
            },
        )
        self.tools = self.Tools(self)