import { useState, useEffect } from 'react';
import axios from 'axios';

export default function YouTubeScraper() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [channels, setChannels] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [channelDetail, setChannelDetail] = useState(null);

  const fetchChannels = async () => {
    try {
      const res = await axios.get('/api/channels/');
      setChannels(res.data);
    } catch (err) {
      console.error('Error fetching channels:', err);
    }
  };

  const fetchTasks = async () => {
    try {
      const res = await axios.get('/api/tasks/');
      setTasks(res.data);
    } catch (err) {
      console.error('Error fetching tasks:', err);
    }
  };

  const fetchChannelDetail = async (id) => {
    try {
      const res = await axios.get(`/api/channels/${id}/`);
      setChannelDetail(res.data);
    } catch (err) {
      console.error('Error fetching channel detail:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post('/api/tasks/scrape_channel/', { channel_url: url });
      setUrl('');
    } catch (err) {
      alert('Failed to submit scraping task');
    } finally {
      setLoading(false);
      await fetchChannels();
      await fetchTasks();
    }
  };

  useEffect(() => {
    fetchChannels();
    fetchTasks();
    const interval = setInterval(fetchTasks, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedId) fetchChannelDetail(selectedId);
  }, [selectedId]);

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="url"
          placeholder="Enter YouTube Channel URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Scraping...' : 'Scrape Channel'}
        </button>
      </form>

      <h2>Channels</h2>
      <ul>
        {channels.length === 0 && <li>No channels yet</li>}
        {channels.map((ch) => (
          <li
            key={ch.id}
            style={{ cursor: 'pointer' }}
            onClick={() => setSelectedId(ch.id)}
          >
            {ch.title} ({ch.videos_count} videos)
          </li>
        ))}
      </ul>

      <h2>Task Status</h2>
      <ul>
        {tasks.length === 0 && <li>No tasks yet</li>}
        {tasks.map((task) => (
          <li key={task.task_id}>
            {task.channel.title} — {task.status}
            {task.status === 'completed' && ` (${task.videos_scraped} videos)`}
            {task.error_message && <span style={{ color: 'red' }}> ⚠ {task.error_message}</span>}
          </li>
        ))}
      </ul>

      {channelDetail && (
        <div>
          <h3>Videos from {channelDetail.title}</h3>
          <ul>
            {channelDetail.videos && channelDetail.videos.length > 0 ? (
              channelDetail.videos.map((vid, i) => (
                <li key={i}>
                  <a href={vid.video_url} target="_blank" rel="noreferrer">
                    {vid.title}
                  </a>
                </li>
              ))
            ) : (
              <li>No videos found</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
