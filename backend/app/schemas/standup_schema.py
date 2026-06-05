"""
Marshmallow schemas handle both:
  1. Input validation (deserialization / load)
  2. Output serialization (dump)

Keeping schemas separate from models keeps models thin and testable.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError, post_load


class StandupPostInputSchema(Schema):
    """Validates multipart/form-data input for POST /api/standups."""

    author = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120),
        error_messages={'required': 'Author name is required.'},
    )
    yesterday = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Please describe what you worked on yesterday.'},
    )
    today = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Please describe what you are doing today.'},
    )
    blockers = fields.Str(load_default='')

    @validates('author')
    def validate_author(self, value, **kwargs):
        # Basic sanitization: strip dangerous chars
        forbidden = ['<', '>', '"', "'", ';', '--']
        for char in forbidden:
            if char in value:
                raise ValidationError('Author name contains invalid characters.')

    @post_load
    def derive_has_blocker(self, data, **kwargs):
        """Auto-derive has_blocker from the blockers text."""
        blockers_text = data.get('blockers', '').strip()
        data['has_blocker'] = bool(blockers_text) and blockers_text.lower() not in (
            'none', 'no blockers', 'n/a', '-', 'nil'
        )
        return data


class StandupPostOutputSchema(Schema):
    """Serializes StandupPost model instances for API responses."""

    id = fields.Int(dump_default=None)
    author = fields.Str()
    yesterday = fields.Str()
    today = fields.Str()
    blockers = fields.Str()
    has_blocker = fields.Bool()
    attachment_url = fields.Method('get_attachment_url')
    weather_condition = fields.Str(allow_none=True)
    temperature = fields.Float(allow_none=True)
    weather_time = fields.Str(allow_none=True)
    created_at = fields.DateTime(format='iso')

    def get_attachment_url(self, obj) -> str | None:
        """Build a full attachment URL from the stored relative path."""
        if not obj.attachment_path:
            return None
        from flask import request
        base = request.host_url.rstrip('/')
        return f'{base}/api/uploads/{obj.attachment_path}'


class StatsOutputSchema(Schema):
    """Serializes aggregated productivity stats."""

    total_posts = fields.Int()
    active_users_count = fields.Int()
    blocker_count = fields.Int()
    posts_per_day = fields.List(fields.Dict())
    blocker_per_day = fields.List(fields.Dict())


standup_input_schema = StandupPostInputSchema()
standup_output_schema = StandupPostOutputSchema()
standup_list_schema = StandupPostOutputSchema(many=True)
stats_schema = StatsOutputSchema()
