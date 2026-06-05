import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import { createStandup, getStandups, getStats } from './api';
import StandupForm from './components/StandupForm';
import StandupList from './components/StandupList';
import StatsPanel from './components/StatsPanel';

const NAIROBI_TIMEZONE = 'Africa/Nairobi';

function formatNairobiDate(dateString) {
  return new Date(dateString).toLocaleString('en-GB', {
    timeZone: NAIROBI_TIMEZONE,
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function deriveStatsFromStandups(posts) {
  const total_posts = posts.length;
  const active_users_count = new Set(posts.map((post) => post.author)).size;
  const blocker_count = posts.filter((post) => post.has_blocker).length;

  const now = new Date();
  const sevenDaysAgo = new Date(now);
  sevenDaysAgo.setDate(now.getDate() - 6);

  const postsPerDay = new Map();
  const blockerPerDay = new Map();
  const postsPerUser = new Map();

  posts.forEach((post) => {
    const date = new Date(post.created_at);
    if (date < sevenDaysAgo) return;
    const key = date.toISOString().slice(0, 10);
    postsPerDay.set(key, (postsPerDay.get(key) || 0) + 1);
    if (post.has_blocker) {
      blockerPerDay.set(key, (blockerPerDay.get(key) || 0) + 1);
    }
    postsPerUser.set(post.author, (postsPerUser.get(post.author) || 0) + 1);
  });

  const buildSeries = (map) => {
    const days = [];
    for (let i = 0; i < 7; i += 1) {
      const day = new Date(sevenDaysAgo);
      day.setDate(sevenDaysAgo.getDate() + i);
      const key = day.toISOString().slice(0, 10);
      days.push({ date: key, count: map.get(key) || 0 });
    }
    return days;
  };

  // Calculate productivity per day
  const productivityPerDay = [];
  for (let i = 0; i < 7; i += 1) {
    const day = new Date(sevenDaysAgo);
    day.setDate(sevenDaysAgo.getDate() + i);
    const key = day.toISOString().slice(0, 10);
    const totalOnDay = postsPerDay.get(key) || 0;
    const blockersOnDay = blockerPerDay.get(key) || 0;
    const score = totalOnDay > 0 ? Math.round(((totalOnDay - blockersOnDay) / totalOnDay) * 100) : 0;
    productivityPerDay.push({ date: key, score });
  }

  // Calculate team productivity score
  const sevenDayPosts = Array.from(postsPerDay.values()).reduce((sum, count) => sum + count, 0);
  const sevenDayBlockers = Array.from(blockerPerDay.values()).reduce((sum, count) => sum + count, 0);
  const teamProductivityScore = sevenDayPosts > 0 ? Math.round(((sevenDayPosts - sevenDayBlockers) / sevenDayPosts) * 100) : 0;

  return {
    total_posts,
    active_users_count,
    blocker_count,
    posts_per_day: buildSeries(postsPerDay),
    blocker_per_day: buildSeries(blockerPerDay),
    productivity_per_day: productivityPerDay,
    posts_per_user: Array.from(postsPerUser.entries())
      .map(([author, count]) => ({ author, count }))
      .sort((a, b) => b.count - a.count),
    team_productivity_score: teamProductivityScore,
  };
}

function App() {
  const [standups, setStandups] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const latestWeather = standups[0];

  function formatWeatherTime(post) {
    return formatNairobiDate(post.weather_time || post.created_at);
  }

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [posts, statsData] = await Promise.all([getStandups(50, 0), getStats()]);
        setStandups(posts);
        setStats(statsData);
      } catch (err) {
        setError(err.message || 'Unable to load data.');
        setStats(deriveStatsFromStandups(standups));
      } finally {
        setLoading(false);
      }
    }

    loadData();

    const socket = io('/feed', {
      path: '/socket.io',
      transports: ['websocket'],
    });

    socket.on('connect', () => {
      console.debug('Connected to backend real-time feed');
    });

    socket.on('new_standup', (post) => {
      setStandups((current) => {
        const next = [post, ...current];
        setStats(deriveStatsFromStandups(next));
        return next;
      });
      getStats().then(setStats).catch(console.error);
    });

    socket.on('connect_error', (err) => {
      console.warn('Real-time connection failed:', err.message);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  async function handleSubmit(formData) {
    setError(null);
    try {
      const newPost = await createStandup(formData);
      setStandups((current) => {
        const next = [newPost, ...current];
        setStats(deriveStatsFromStandups(next));
        return next;
      });
      const updatedStats = await getStats();
      setStats(updatedStats);
      return { success: true };
    } catch (err) {
      return { success: false, message: err.message || 'Submission failed', errors: err.errors };
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-copy">
          <p className="company-name">
            <span className="company-blue">KONVERGENZ</span>{' '}
            <span className="company-red">NETWORK SOLUTIONS</span>
          </p>
          <p className="eyebrow">Team Standup Logger</p>
          <h1>Daily Standups &amp; Productivity Snapshot</h1>
          <p className="subtitle">Submit your daily update, view recent posts, and track blocker trends in real time.</p>
        </div>

        <div className="weather-card">
          <span className="weather-label">Latest weather</span>
          <div className="weather-top">
            <strong className="weather-temp">
              {latestWeather?.temperature !== null && latestWeather?.temperature !== undefined
                ? `${latestWeather.temperature.toFixed(1)}°C`
                : '--'}
            </strong>
            <span className="weather-condition">{latestWeather?.weather_condition || 'Pending'}</span>
          </div>
          <p className="weather-author">
            {latestWeather ? `Updated by ${latestWeather.author}` : 'Waiting for the first standup'}
          </p>
          {latestWeather ? (
            <p className="weather-time">
              {formatWeatherTime(latestWeather)} (Nairobi time)
            </p>
          ) : null}
        </div>
      </header>

      <main>
        <div className="content-grid">
          <section className="panel panel-form">
            <div className="panel-title-row">
              <h2>Submit Standup</h2>
              <span className="panel-tag">Live</span>
            </div>
            <StandupForm onSubmit={handleSubmit} />
          </section>

          <section className="panel panel-stats">
            <div className="panel-title-row">
              <h2>Team stats</h2>
              <span className="panel-tag success">Real-time</span>
            </div>
            {stats ? <StatsPanel stats={stats} /> : <p>Loading stats...</p>}
          </section>
        </div>

        <section className="panel panel-list">
          <div className="panel-heading">
            <h2>Recent standup posts</h2>
            <div className="panel-heading-right">
              {loading && <span className="badge">Loading...</span>}
              {error && <span className="error-message">{error}</span>}
            </div>
          </div>
          <StandupList standups={standups} />
        </section>
      </main>
    </div>
  );
}

export default App;
