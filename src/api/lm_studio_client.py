"""
LM Studio API client for REST API communication.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator, Callable
import aiohttp
import requests
from datetime import datetime

from models.message import Message, MessageRole
from utils.config import ConfigManager


class LMStudioAPIError(Exception):
    """Custom exception for LM Studio API errors."""
    pass


class LMStudioClient:
    """
    Client for communicating with LM Studio's REST API.

    This client handles both synchronous and asynchronous requests to the LM Studio server,
    supporting model listing, chat completions, and streaming responses.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the LM Studio client.

        Args:
            config_manager (ConfigManager): Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def api_config(self):
        """Get API configuration."""
        return self.config_manager.api_config

    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'GenAI-Desktop/1.0.0'
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create async HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.api_config.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._get_headers()
            )
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def test_connection(self) -> bool:
        """
        Test connection to LM Studio server.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = requests.get(
                self.api_config.models_endpoint,
                headers=self._get_headers(),
                timeout=self.api_config.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from LM Studio.

        Returns:
            List[Dict[str, Any]]: List of available models

        Raises:
            LMStudioAPIError: If the API request fails
        """
        try:
            response = requests.get(
                self.api_config.models_endpoint,
                headers=self._get_headers(),
                timeout=self.api_config.timeout
            )
            response.raise_for_status()

            data = response.json()
            models = data.get('data', [])

            self.logger.info(f"Retrieved {len(models)} models from LM Studio")
            return models

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get models: {e}")
            raise LMStudioAPIError(f"Failed to get models: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise LMStudioAPIError(f"Invalid JSON response: {e}")

    def send_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to LM Studio.

        Args:
            messages (List[Dict[str, str]]): List of messages in conversation
            model (str): Model name to use
            temperature (float): Temperature for generation (0.0 to 1.0)
            max_tokens (int): Maximum tokens to generate
            stream (bool): Whether to stream the response
            **kwargs: Additional parameters for the API

        Returns:
            Dict[str, Any]: API response

        Raises:
            LMStudioAPIError: If the API request fails
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs
        }

        try:
            response = requests.post(
                self.api_config.completions_endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=self.api_config.timeout,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                return {"response": response}
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Chat completion failed: {e}")
            raise LMStudioAPIError(f"Chat completion failed: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise LMStudioAPIError(f"Invalid JSON response: {e}")

    async def send_chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send an async chat completion request to LM Studio.

        Args:
            messages (List[Dict[str, str]]): List of messages in conversation
            model (str): Model name to use
            temperature (float): Temperature for generation (0.0 to 1.0)
            max_tokens (int): Maximum tokens to generate
            stream (bool): Whether to stream the response
            **kwargs: Additional parameters for the API

        Returns:
            Dict[str, Any]: API response

        Raises:
            LMStudioAPIError: If the API request fails
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs
        }

        try:
            session = await self._get_session()
            async with session.post(
                self.api_config.completions_endpoint,
                json=payload
            ) as response:
                response.raise_for_status()

                if stream:
                    return {"response": response}
                else:
                    return await response.json()

        except aiohttp.ClientError as e:
            self.logger.error(f"Async chat completion failed: {e}")
            raise LMStudioAPIError(f"Async chat completion failed: {e}")

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion response from LM Studio.

        Args:
            messages (List[Dict[str, str]]): List of messages in conversation
            model (str): Model name to use
            temperature (float): Temperature for generation (0.0 to 1.0)
            max_tokens (int): Maximum tokens to generate
            callback (Optional[Callable[[str], None]]): Callback for each chunk
            **kwargs: Additional parameters for the API

        Yields:
            str: Chunks of the generated response

        Raises:
            LMStudioAPIError: If the API request fails
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }

        try:
            session = await self._get_session()
            async with session.post(
                self.api_config.completions_endpoint,
                json=payload
            ) as response:
                response.raise_for_status()

                full_content = ""
                async for line in response.content:
                    line = line.decode('utf-8').strip()

                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix

                        if data_str == '[DONE]':
                            break

                        try:
                            data = json.loads(data_str)
                            choices = data.get('choices', [])

                            if choices:
                                delta = choices[0].get('delta', {})
                                content = delta.get('content', '')

                                if content:
                                    full_content += content
                                    if callback:
                                        callback(content)
                                    yield content

                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue

        except aiohttp.ClientError as e:
            self.logger.error(f"Streaming chat completion failed: {e}")
            raise LMStudioAPIError(f"Streaming chat completion failed: {e}")

    def parse_streaming_response(self, response_stream) -> AsyncGenerator[str, None]:
        """
        Parse streaming response from LM Studio API.

        Args:
            response_stream: Response stream from requests

        Yields:
            str: Chunks of the generated response
        """
        try:
            for line in response_stream.iter_lines():
                if line:
                    line = line.decode('utf-8').strip()

                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix

                        if data_str == '[DONE]':
                            break

                        try:
                            data = json.loads(data_str)
                            choices = data.get('choices', [])

                            if choices:
                                delta = choices[0].get('delta', {})
                                content = delta.get('content', '')

                                if content:
                                    yield content

                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue

        except Exception as e:
            self.logger.error(f"Error parsing streaming response: {e}")
            raise LMStudioAPIError(f"Error parsing streaming response: {e}")

    def create_message_from_response(
        self,
        response: Dict[str, Any],
        model_name: str,
        temperature: float,
        max_tokens: int
    ) -> Message:
        """
        Create a Message object from API response.

        Args:
            response (Dict[str, Any]): API response
            model_name (str): Model name used
            temperature (float): Temperature used
            max_tokens (int): Max tokens used

        Returns:
            Message: Created message object
        """
        choices = response.get('choices', [])
        if not choices:
            raise LMStudioAPIError("No choices in response")

        choice = choices[0]
        message_data = choice.get('message', {})
        content = message_data.get('content', '')

        # Extract usage information if available
        usage = response.get('usage', {})
        token_count = usage.get('completion_tokens')

        return Message(
            content=content,
            role=MessageRole.ASSISTANT,
            timestamp=datetime.now(),
            token_count=token_count,
            model_used=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific model.

        Args:
            model_name (str): Name of the model

        Returns:
            Optional[Dict[str, Any]]: Model information or None if not found
        """
        try:
            models = self.get_available_models()
            for model in models:
                if model.get('id') == model_name:
                    return model
            return None
        except LMStudioAPIError:
            return None

    def validate_model_parameters(
        self,
        model_name: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """
        Validate model parameters against model capabilities.

        Args:
            model_name (str): Model name
            temperature (float): Temperature value
            max_tokens (int): Max tokens value

        Returns:
            Dict[str, Any]: Validation results with adjusted parameters if needed
        """
        # Basic validation
        temperature = max(0.0, min(1.0, temperature))
        max_tokens = max(1, min(4096, max_tokens))  # Reasonable limits

        # Get model info for more specific validation
        model_info = self.get_model_info(model_name)
        if model_info:
            # Adjust based on model-specific limits if available
            context_length = model_info.get('context_length')
            if context_length:
                max_tokens = min(max_tokens, context_length)

        return {
            'temperature': temperature,
            'max_tokens': max_tokens,
            'model_name': model_name,
            'valid': True
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._session and not self._session.closed:
            # Can't await in sync context, so we create a new event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If there's already a running loop, schedule the close
                    asyncio.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except RuntimeError:
                # Create new event loop if none exists
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.close())
                loop.close()
