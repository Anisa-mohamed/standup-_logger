"""
StandupService encapsulates all business logic for standup operations.

Keeping logic here (not in routes) makes it:
- Testable without HTTP context
- Reusable by WebSocket handlers and CLI scripts
- Easy to swap persistence layer later
"""
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from app.extensions import db
from app.models.standup import StandupPost
from app.services.weather_service import fetch_current_weather
from app.utils.file_upload import save_upload

logger = logging.getLogger(__name__)


class StandupService:

    @staticmethod
    def create_standup(validated_data: dict, file_storage=None) -> StandupPost:
        """
        Persist a new standup post.

        Steps:
          1. Save optional file upload
          2. Fetch weather (never blocks on failure)
          3. Create and commit the DB record
        """
        # 1. Handle file upload
        attachment_path = None
        if file_storage:
            attachment_path = save_upload(file_storage)  # raises ValueError on bad type

        # 2. Weather enrichment
        weather = fetch_current_weather()

        # 3. Persist
        post = StandupPost(
            author=validated_data['author'].strip(),
            yesterday=validated_data['yesterday'].strip(),
            today=validated_data['today'].strip(),
            blockers=validated_data.get('blockers', '').strip(),
            has_blocker=validated_data.get('has_blocker', False),
            attachment_path=attachment_path,
            temperature=weather.get('temperature'),
            weather_condition=weather.get('weather_condition'),
            weather_time=weather.get('weather_time'),
        )
        db.session.add(post)
        db.session.commit()
        logger.info('New standup created: id=%s author=%s', post.id, post.author)
        return post

    @staticmethod
    def get_all_standups(limit: int = 100, offset: int = 0):
        """Return standups ordered newest-first with pagination."""
        return (
            StandupPost.query
            .order_by(StandupPost.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_stats() -> dict:
        """
        Aggregate stats for the last 7 days.

        Returns:
            {
                total_posts, active_users_count, blocker_count,
                posts_per_day: [{date, count}, ...],
                blocker_per_day: [{date, count}, ...],
                productivity_per_day: [{date, score}, ...],  # score 0-100
                posts_per_user: [{author, count}, ...],
                team_productivity_score: 0-100  # % of blocker-free posts
            }
        """
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)

        # SQLite-compatible date truncation
        date_col = func.date(StandupPost.created_at)

        posts_per_day = (
            db.session.query(date_col.label('date'), func.count().label('count'))
            .filter(StandupPost.created_at >= seven_days_ago)
            .group_by(date_col)
            .order_by(date_col)
            .all()
        )

        blocker_per_day = (
            db.session.query(date_col.label('date'), func.count().label('count'))
            .filter(
                StandupPost.created_at >= seven_days_ago,
                StandupPost.has_blocker == True,
            )
            .group_by(date_col)
            .order_by(date_col)
            .all()
        )

        total_posts = StandupPost.query.count()
        active_users = db.session.query(
            func.count(func.distinct(StandupPost.author))
        ).scalar()

        blocker_count = StandupPost.query.filter(
            StandupPost.created_at >= seven_days_ago,
            StandupPost.has_blocker == True,
        ).count()

        # Calculate productivity score per day (% of blocker-free posts)
        productivity_per_day = []
        posts_dict = {str(r.date): r.count for r in posts_per_day}
        blockers_dict = {str(r.date): r.count for r in blocker_per_day}

        for r in posts_per_day:
            date_str = str(r.date)
            total_on_day = r.count
            blockers_on_day = blockers_dict.get(date_str, 0)
            blocker_free_posts = total_on_day - blockers_on_day
            score = round((blocker_free_posts / total_on_day * 100)) if total_on_day > 0 else 0
            productivity_per_day.append({'date': date_str, 'score': score})

        # Get posts per user for last 7 days
        posts_per_user = (
            db.session.query(
                StandupPost.author.label('author'),
                func.count().label('count')
            )
            .filter(StandupPost.created_at >= seven_days_ago)
            .group_by(StandupPost.author)
            .order_by(func.count().desc())
            .all()
        )

        # Calculate overall team productivity score
        seven_day_posts = StandupPost.query.filter(
            StandupPost.created_at >= seven_days_ago
        ).count()
        team_productivity_score = 0
        if seven_day_posts > 0:
            blocker_free_count = seven_day_posts - blocker_count
            team_productivity_score = round((blocker_free_count / seven_day_posts) * 100)

        return {
            'total_posts': total_posts,
            'active_users_count': active_users,
            'blocker_count': blocker_count,
            'posts_per_day': [{'date': str(r.date), 'count': r.count} for r in posts_per_day],
            'blocker_per_day': [{'date': str(r.date), 'count': r.count} for r in blocker_per_day],
            'productivity_per_day': productivity_per_day,
            'posts_per_user': [{'author': r.author, 'count': r.count} for r in posts_per_user],
            'team_productivity_score': team_productivity_score,
        }
