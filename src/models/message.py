"""
Message data model for chat messages.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class MessageRole(Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """
    Represents a single chat message.

    Attributes:
        content (str): The text content of the message
        role (MessageRole): The role of the message sender (user, assistant, system)
        timestamp (datetime): When the message was created
        message_id (str): Unique identifier for the message
        token_count (Optional[int]): Number of tokens in the message (if available)
        model_used (Optional[str]): The model that generated this message (for assistant messages)
        temperature (Optional[float]): Temperature used for generation (for assistant messages)
        max_tokens (Optional[int]): Max tokens limit used for generation
    """
    content: str
    role: MessageRole
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))
    token_count: Optional[int] = None
    model_used: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert message to dictionary format."""
        return {
            'content': self.content,
            'role': self.role.value,
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id,
            'token_count': self.token_count,
            'model_used': self.model_used,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create message from dictionary format."""
        return cls(
            content=data['content'],
            role=MessageRole(data['role']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            message_id=data.get('message_id', str(datetime.now().timestamp())),
            token_count=data.get('token_count'),
            model_used=data.get('model_used'),
            temperature=data.get('temperature'),
            max_tokens=data.get('max_tokens')
        )

    def to_api_format(self) -> dict:
        """Convert to format expected by LM Studio API."""
        return {
            'role': self.role.value,
            'content': self.content
        }

    def is_user_message(self) -> bool:
        """Check if this is a user message."""
        return self.role == MessageRole.USER

    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message."""
        return self.role == MessageRole.ASSISTANT

    def is_system_message(self) -> bool:
        """Check if this is a system message."""
        return self.role == MessageRole.SYSTEM

    def get_display_time(self) -> str:
        """Get formatted timestamp for display."""
        return self.timestamp.strftime("%H:%M:%S")

    def get_display_date(self) -> str:
        """Get formatted date for display."""
        return self.timestamp.strftime("%Y-%m-%d")

    def __str__(self) -> str:
        """String representation of the message."""
        return f"[{self.role.value.upper()}] {self.content[:50]}{'...' if len(self.content) > 50 else ''}"
