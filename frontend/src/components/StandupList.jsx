function formatNairobiDate(dateString) {
  return new Date(dateString).toLocaleString('en-GB', {
    timeZone: 'Africa/Nairobi',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function StandupList({ standups }) {
  if (!standups?.length) {
    return <p className="empty-state">No standup posts yet. Submit the first update!</p>;
  }

  return (
    <div className="standup-list">
      {standups.map((post) => (
        <article key={post.id} className="standup-card">
          <div className="standup-card-header">
            <div>
              <h3>{post.author}</h3>
              <p className="meta">{formatNairobiDate(post.created_at)}</p>
            </div>
            {post.has_blocker && <span className="pill pill-warning">Blocker</span>}
          </div>

          <div className="standup-section">
            <strong>Yesterday</strong>
            <p>{post.yesterday}</p>
          </div>

          <div className="standup-section">
            <strong>Today</strong>
            <p>{post.today}</p>
          </div>

          {post.blockers ? (
            <div className="standup-section">
              <strong>Blockers</strong>
              <p>{post.blockers}</p>
            </div>
          ) : null}

          {post.attachment_url ? (
            <div className="standup-section">
              <strong>Attachment</strong>
              <a href={post.attachment_url} target="_blank" rel="noreferrer">
                View attachment
              </a>
            </div>
          ) : null}

          {(post.weather_condition || post.temperature !== null) && (
            <div className="standup-footer">
              <span>{post.weather_condition || 'Weather data unavailable'}</span>
              {post.temperature !== null && <span>{post.temperature.toFixed(1)}°C</span>}
            </div>
          )}
        </article>
      ))}
    </div>
  );
}

export default StandupList;
