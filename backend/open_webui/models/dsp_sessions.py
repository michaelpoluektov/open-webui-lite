import time
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, JSON, BigInteger
from open_webui.internal.db import Base, get_db


class DspSession(Base):
    __tablename__ = "dsp_session"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    graph = Column(JSON)
    forked_graph = Column(JSON)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class DspSessionModel(BaseModel):
    id: str
    user_id: str
    graph: dict
    forked_graph: dict
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


class DspSessionsTable:
    def create_session(self, session_id: str, user_id: str) -> DspSessionModel:
        """Create a new DSP session for a user."""
        current_time = int(time.time())
        session = DspSessionModel(
            id=session_id,
            user_id=user_id,
            graph={},
            forked_graph={},
            created_at=current_time,
            updated_at=current_time,
        )

        with get_db() as db:
            db_session = DspSession(**session.model_dump())
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            return DspSessionModel.model_validate(db_session)

    def get_session(self, session_id: str, user_id: str) -> Optional[DspSessionModel]:
        """Get a DSP session by ID and user ID."""
        with get_db() as db:
            session = (
                db.query(DspSession).filter_by(id=session_id, user_id=user_id).first()
            )
            return DspSessionModel.model_validate(session) if session else None

    def update_session(
        self, session_id: str, user_id: str, graph: dict, forked_graph: dict
    ) -> Optional[DspSessionModel]:
        """Update a DSP session's graphs."""
        with get_db() as db:
            session = (
                db.query(DspSession).filter_by(id=session_id, user_id=user_id).first()
            )
            if not session:
                return None

            session.graph = graph
            session.forked_graph = forked_graph
            session.updated_at = int(time.time())
            db.commit()
            db.refresh(session)
            return DspSessionModel.model_validate(session)

    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a DSP session."""
        with get_db() as db:
            result = (
                db.query(DspSession).filter_by(id=session_id, user_id=user_id).delete()
            )
            db.commit()
            return result > 0

    def get_user_sessions(self, user_id: str) -> list[DspSessionModel]:
        """Get all DSP sessions for a user."""
        with get_db() as db:
            sessions = db.query(DspSession).filter_by(user_id=user_id).all()
            return [DspSessionModel.model_validate(session) for session in sessions]


DspSessions = DspSessionsTable()

