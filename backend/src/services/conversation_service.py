"""Conversation service for chat session and message management.

Handles conversation creation, message persistence, and history retrieval.
All operations are scoped to a specific user for isolation.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Session, col, select

from src.models.conversation import Conversation
from src.models.message import Message


class ConversationService:
    """Service for conversation and message operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_conversation(
        self,
        user_id: uuid.UUID,
        title: Optional[str] = None,
    ) -> Conversation:
        """Create a new conversation for a user."""
        now = datetime.utcnow()
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Conversation]:
        """Get a conversation by ID, filtered by user ownership."""
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        return self.session.exec(statement).first()

    def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        tool_calls: Optional[list[dict]] = None,
    ) -> Message:
        """Add a message to a conversation.

        Automatically assigns the next sequence number and
        updates the conversation's updated_at timestamp.
        """
        # Get next sequence number
        statement = (
            select(Message.sequence_number)
            .where(Message.conversation_id == conversation_id)
            .order_by(col(Message.sequence_number).desc())
            .limit(1)
        )
        last_seq = self.session.exec(statement).first()
        next_seq = (last_seq or 0) + 1

        message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            sequence_number=next_seq,
            created_at=datetime.utcnow(),
        )
        self.session.add(message)

        # Update conversation timestamp
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_recent_messages(
        self,
        conversation_id: uuid.UUID,
        limit: int = 50,
        before_sequence: Optional[int] = None,
    ) -> list[Message]:
        """Get the most recent messages for a conversation.

        Returns messages ordered by sequence_number ascending
        (oldest first within the window).
        """
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        )

        if before_sequence is not None:
            statement = statement.where(
                Message.sequence_number < before_sequence
            )

        # Get the last N messages (descending), then reverse for
        # chronological order
        statement = (
            statement.order_by(col(Message.sequence_number).desc())
            .limit(limit)
        )
        messages = list(self.session.exec(statement).all())
        messages.reverse()
        return messages

    def list_conversations(
        self,
        user_id: uuid.UUID,
    ) -> list[Conversation]:
        """List all conversations for a user, newest first."""
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(col(Conversation.updated_at).desc())
        )
        return list(self.session.exec(statement).all())


def get_conversation_service(session: Session) -> ConversationService:
    """Factory function to create ConversationService instance."""
    return ConversationService(session)
