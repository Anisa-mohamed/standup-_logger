import ProductivityChart from './ProductivityChart';

function StatsPanel({ stats }) {
  const maxCount = Math.max(
    ...stats.posts_per_day.map((entry) => entry.count),
    1,
  );

  return (
    <div className="stats-panel">
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-value">{stats.total_posts}</span>
          <span className="stat-label">Total posts</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.active_users_count}</span>
          <span className="stat-label">Active users</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.blocker_count}</span>
          <span className="stat-label">Blocker posts</span>
        </div>
      </div>

      <ProductivityChart stats={stats} />

      <div className="chart-group">
        <div className="chart-card chart-card-wide">
          <h3>Posts in the last 7 days</h3>
          <ul>
            {stats.posts_per_day.map((entry) => (
              <li key={entry.date}>
                <span>{entry.date}</span>
                <div className="bar-row">
                  <div className="bar-fill" style={{ width: `${(entry.count / maxCount) * 100}%` }} />
                  <strong>{entry.count}</strong>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div className="chart-card chart-card-wide">
          <h3>Blockers in the last 7 days</h3>
          <ul>
            {stats.blocker_per_day.map((entry) => (
              <li key={entry.date}>
                <span>{entry.date}</span>
                <div className="bar-row">
                  <div className="bar-fill blocker" style={{ width: `${(entry.count / maxCount) * 100}%` }} />
                  <strong>{entry.count}</strong>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default StatsPanel;
