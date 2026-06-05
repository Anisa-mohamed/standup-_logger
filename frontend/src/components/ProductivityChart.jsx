/**
 * ProductivityChart displays team productivity metrics:
 * - Overall team productivity score (0-100%)
 * - Daily productivity trend for last 7 days
 * - Posts per team member breakdown
 */
function ProductivityChart({ stats }) {
  if (!stats || !stats.productivity_per_day) {
    return null;
  }

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // amber
    if (score >= 40) return '#ef4444'; // red
    return '#6b7280'; // gray
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  const maxProductivity = Math.max(
    ...stats.productivity_per_day.map((entry) => entry.score),
    100,
  );

  const totalPostsPerUser = (stats.posts_per_user || []).reduce((sum, entry) => sum + entry.count, 0);

  return (
    <div className="productivity-chart">
      {/* Overall Team Productivity Score */}
      <div className="chart-card chart-card-wide">
        <h3>Team Productivity Score</h3>
        <div className="productivity-score-container">
          <div className="productivity-score-circle">
            <div
              className="productivity-score-inner"
              style={{
                borderColor: getScoreColor(stats.team_productivity_score),
              }}
            >
              <div className="productivity-score-value">{stats.team_productivity_score}%</div>
              <div className="productivity-score-label">
                {getScoreLabel(stats.team_productivity_score)}
              </div>
            </div>
          </div>
          <div className="productivity-score-info">
            <p>
              <strong>{stats.team_productivity_score}% of posts</strong> submitted in the last 7
              days were blocker-free
            </p>
            <p className="text-muted">
              {totalPostsPerUser > 0 ? `Out of ${totalPostsPerUser} total posts` : 'No data available'}
            </p>
          </div>
        </div>
      </div>

      {/* Daily Productivity Trend */}
      <div className="chart-card chart-card-wide">
        <h3>Daily Productivity Trend</h3>
        <ul>
          {stats.productivity_per_day.map((entry) => (
            <li key={entry.date}>
              <span>{entry.date}</span>
              <div className="bar-row">
                <div
                  className="bar-fill productivity"
                  style={{
                    width: `${(entry.score / maxProductivity) * 100}%`,
                    backgroundColor: getScoreColor(entry.score),
                  }}
                />
                <strong>{entry.score}%</strong>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Posts per Team Member */}
      {stats.posts_per_user && stats.posts_per_user.length > 0 && (
        <div className="chart-card chart-card-wide">
          <h3>Posts per Team Member (Last 7 Days)</h3>
          <ul>
            {stats.posts_per_user.map((entry) => (
              <li key={entry.author}>
                <span>{entry.author}</span>
                <div className="bar-row">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${(entry.count / Math.max(...stats.posts_per_user.map((e) => e.count), 1)) * 100}%`,
                    }}
                  />
                  <strong>{entry.count}</strong>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ProductivityChart;
