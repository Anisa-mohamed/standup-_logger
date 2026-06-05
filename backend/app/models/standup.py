"""
StandupPost model — core data entity for the Team Standup Logger.

Design decisions:
- has_blocker is a denormalized boolean for fast stats queries without full-text scans.
- attachment_path stores only the relative path; the absolute URL is built at serialization time.
- weather fields are nullable so a failed API call never blocks a submission.
"""
from datetime import datetime, timezone
from app.extensions import db


class StandupPost(db.Model):
    __tablename__ = 'standup_posts'

    id = db.Column(db.Integer, primary_key=True)

    # Author information
    author = db.Column(db.String(120), nullable=False, index=True)

    # Standup content
    yesterday = db.Column(db.Text, nullable=False)
    today = db.Column(db.Text, nullable=False)
    blockers = db.Column(db.Text, nullable=True)
    has_blocker = db.Column(db.Boolean, default=False, nullable=False)

    # Optional file attachment (relative path inside UPLOAD_FOLDER)
    attachment_path = db.Column(db.String(255), nullable=True)

    # Weather snapshot at submission time
    weather_condition = db.Column(db.String(100), nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    weather_time = db.Column(db.String(50), nullable=True)

    # Timestamps
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self):
        return f'<StandupPost id={self.id} author={self.author} date={self.created_at.date()}>'

    def to_dict(self, attachment_base_url: str = '') -> dict:
        """Lightweight serialization used internally; prefer Marshmallow schemas for API responses."""
        return {
            'id': self.id,
            'author': self.author,
            'yesterday': self.yesterday,
            'today': self.today,
            'blockers': self.blockers,
            'has_blocker': self.has_blocker,
            'attachment_url': (
                f'{attachment_base_url}/{self.attachment_path}' if self.attachment_path else None
            ),
            'weather_condition': self.weather_condition,
            'temperature': self.temperature,
            'created_at': self.created_at.isoformat(),
        }
