"""
ChatSession data model for managing chat sessions with conversation history.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path

from models.message import Message, MessageRole


@dataclass
class ChatSession:
    """
    Represents a chat session with conversation history.

    Attributes:
        session_id (str): Unique identifier for the session
        title (str): Display title for the session
        messages (List[Message]): List of messages in the conversation
        created_at (datetime): When the session was created
        updated_at (datetime): When the session was last updated
        model_name (Optional[str]): The LLM model used in this session
        persona (str): The persona/role being used (e.g., "Software Engineer", "User")
        system_prompt (Optional[str]): System prompt for the persona
        default_temperature (float): Default temperature setting for this session
        default_max_tokens (int): Default max tokens setting for this session
        metadata (Dict[str, Any]): Additional metadata for the session
    """
    session_id: str
    title: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    model_name: Optional[str] = None
    persona: str = "User"
    system_prompt: Optional[str] = None
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize session after creation."""
        if not self.messages and self.system_prompt:
            # Add system message if system prompt is provided
            system_msg = Message(
                content=self.system_prompt,
                role=MessageRole.SYSTEM,
                model_used=self.model_name
            )
            self.messages.insert(0, system_msg)

    def add_message(self, message: Message) -> None:
        """
        Add a message to the session.

        Args:
            message (Message): The message to add
        """
        self.messages.append(message)
        self.updated_at = datetime.now()

        # Update title if this is the first user message and title is default
        if (message.is_user_message() and
            len([m for m in self.messages if m.is_user_message()]) == 1 and
            self.title.startswith("New Chat")):
            # Set title to first 50 characters of first user message
            self.title = message.content[:50] + ("..." if len(message.content) > 50 else "")

    def get_conversation_history(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get conversation history in API format.

        Args:
            include_system (bool): Whether to include system messages

        Returns:
            List[Dict[str, str]]: Messages in API format
        """
        messages = self.messages
        if not include_system:
            messages = [m for m in messages if not m.is_system_message()]

        return [message.to_api_format() for message in messages]

    def get_last_n_messages(self, n: int, include_system: bool = False) -> List[Message]:
        """
        Get the last N messages from the conversation.

        Args:
            n (int): Number of messages to retrieve
            include_system (bool): Whether to include system messages

        Returns:
            List[Message]: Last N messages
        """
        messages = self.messages
        if not include_system:
            messages = [m for m in messages if not m.is_system_message()]

        return messages[-n:] if n > 0 else messages

    def clear_conversation(self, keep_system: bool = True) -> None:
        """
        Clear all messages from the conversation.

        Args:
            keep_system (bool): Whether to keep system messages
        """
        if keep_system:
            self.messages = [m for m in self.messages if m.is_system_message()]
        else:
            self.messages = []

        self.updated_at = datetime.now()

    def update_system_prompt(self, system_prompt: str) -> None:
        """
        Update the system prompt for this session.

        Args:
            system_prompt (str): New system prompt
        """
        self.system_prompt = system_prompt

        # Remove existing system messages
        self.messages = [m for m in self.messages if not m.is_system_message()]

        # Add new system message at the beginning
        if system_prompt:
            system_msg = Message(
                content=system_prompt,
                role=MessageRole.SYSTEM,
                model_used=self.model_name
            )
            self.messages.insert(0, system_msg)

        self.updated_at = datetime.now()

    def get_message_count(self) -> Dict[str, int]:
        """
        Get count of messages by role.

        Returns:
            Dict[str, int]: Count of messages by role
        """
        counts = {"user": 0, "assistant": 0, "system": 0}
        for message in self.messages:
            counts[message.role.value] += 1
        return counts

    def get_total_tokens(self) -> int:
        """
        Get total token count for the session.

        Returns:
            int: Total token count (if available)
        """
        total = 0
        for message in self.messages:
            if message.token_count:
                total += message.token_count
        return total

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary format for serialization."""
        return {
            'session_id': self.session_id,
            'title': self.title,
            'messages': [message.to_dict() for message in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'model_name': self.model_name,
            'persona': self.persona,
            'system_prompt': self.system_prompt,
            'default_temperature': self.default_temperature,
            'default_max_tokens': self.default_max_tokens,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create session from dictionary format."""
        messages = [Message.from_dict(msg_data) for msg_data in data.get('messages', [])]

        return cls(
            session_id=data['session_id'],
            title=data['title'],
            messages=messages,
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            model_name=data.get('model_name'),
            persona=data.get('persona', 'User'),
            system_prompt=data.get('system_prompt'),
            default_temperature=data.get('default_temperature', 0.7),
            default_max_tokens=data.get('default_max_tokens', 1000),
            metadata=data.get('metadata', {})
        )

    def save_to_file(self, file_path: str) -> None:
        """
        Save session to JSON file.

        Args:
            file_path (str): Path to save the session file
        """
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'ChatSession':
        """
        Load session from JSON file.

        Args:
            file_path (str): Path to the session file

        Returns:
            ChatSession: Loaded session
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return cls.from_dict(data)

    def export_to_text(self) -> str:
        """
        Export conversation to plain text format.

        Returns:
            str: Conversation in text format
        """
        lines = []
        lines.append(f"Chat Session: {self.title}")
        lines.append(f"Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Model: {self.model_name or 'Unknown'}")
        lines.append(f"Persona: {self.persona}")
        lines.append("-" * 80)
        lines.append("")

        for message in self.messages:
            if message.is_system_message():
                lines.append(f"[SYSTEM] {message.content}")
            elif message.is_user_message():
                lines.append(f"[USER - {message.get_display_time()}] {message.content}")
            else:  # assistant message
                lines.append(f"[ASSISTANT - {message.get_display_time()}] {message.content}")
            lines.append("")

        return "\n".join(lines)

    def get_summary(self) -> str:
        """
        Get a summary of the session.

        Returns:
            str: Session summary
        """
        message_counts = self.get_message_count()
        total_tokens = self.get_total_tokens()

        summary_parts = [
            f"Messages: {message_counts['user']} user, {message_counts['assistant']} assistant"
        ]

        if total_tokens > 0:
            summary_parts.append(f"Tokens: {total_tokens}")

        if self.model_name:
            summary_parts.append(f"Model: {self.model_name}")

        return " | ".join(summary_parts)

    def __str__(self) -> str:
        """String representation of the session."""
        return f"ChatSession(id={self.session_id}, title='{self.title}', messages={len(self.messages)})"
