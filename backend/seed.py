"""
Seed the database with realistic sample standup data.

Usage:
    python seed.py

Run AFTER flask db upgrade.
"""
import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models.standup import StandupPost

SAMPLE_STANDUPS = [
    {
        'author': 'Alice Mwangi',
        'yesterday': 'Completed the user authentication flow and wrote unit tests for the login endpoint.',
        'today': 'Working on the dashboard charts and integrating the stats API.',
        'blockers': '',
        'has_blocker': False,
        'weather_condition': 'Partly cloudy',
        'temperature': 22.3,
    },
    {
        'author': 'Brian Otieno',
        'yesterday': 'Fixed the file upload bug that was causing 500 errors on large PDFs.',
        'today': 'Reviewing pull requests and writing documentation for the upload API.',
        'blockers': 'Waiting for design team to share updated Figma mockups.',
        'has_blocker': True,
        'weather_condition': 'Clear sky',
        'temperature': 24.1,
    },
    {
        'author': 'Carol Njeri',
        'yesterday': 'Set up the CI/CD pipeline on GitHub Actions and configured deployment to Render.',
        'today': 'Adding integration tests for the standup submission flow.',
        'blockers': '',
        'has_blocker': False,
        'weather_condition': 'Overcast',
        'temperature': 19.8,
    },
    {
        'author': 'David Kamau',
        'yesterday': 'Implemented the Socket.IO real-time feed and tested with two browser tabs.',
        'today': 'Polishing the frontend standup card UI and adding skeleton loaders.',
        'blockers': 'Socket.IO occasionally drops connection on mobile — investigating.',
        'has_blocker': True,
        'weather_condition': 'Light drizzle',
        'temperature': 17.5,
    },
    {
        'author': 'Alice Mwangi',
        'yesterday': 'Finished the dashboard charts — bar chart for posts per day, line chart for blockers.',
        'today': 'Writing end-to-end tests with Playwright.',
        'blockers': '',
        'has_blocker': False,
        'weather_condition': 'Mainly clear',
        'temperature': 23.0,
    },
]


def seed():
    app = create_app()
    with app.app_context():
        existing = StandupPost.query.count()
        if existing > 0:
            print(f'Database already has {existing} records. Skipping seed.')
            return

        now = datetime.now(timezone.utc)
        for i, data in enumerate(SAMPLE_STANDUPS):
            post = StandupPost(
                **data,
                created_at=now - timedelta(days=len(SAMPLE_STANDUPS) - i - 1),
            )
            db.session.add(post)

        db.session.commit()
        print(f'Seeded {len(SAMPLE_STANDUPS)} sample standup posts.')


if __name__ == '__main__':
    seed()
