import { useState } from 'react';
import axios from 'axios';

export default function ChannelForm({ onSuccess }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post('/api/tasks/scrape_channel/', { channel_url: url });
      setUrl('');
      onSuccess();
    } catch (err) {
      alert('Failed to submit channel');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="url"
        value={url}
        placeholder="Enter YouTube Channel URL"
        onChange={(e) => setUrl(e.target.value)}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Scraping...' : 'Scrape Channel'}
      </button>
    </form>
  );
}
