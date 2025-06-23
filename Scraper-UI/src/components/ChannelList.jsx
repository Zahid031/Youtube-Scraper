import { useEffect, useState } from 'react';
import axios from 'axios';
import ChannelDetail from './ChannelDetail';

export default function ChannelList() {
  const [channels, setChannels] = useState([]);
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    axios.get('/api/channels/').then((res) => setChannels(res.data));
  }, []);

  return (
    <div>
      <h2>Scraped Channels</h2>
      <ul>
        {channels.map((ch) => (
          <li key={ch.id} onClick={() => setSelectedId(ch.id)}>
            {ch.title} ({ch.videos_count} videos)
            <span> - {ch.subscriber_count} subscribers</span>
            <span> - {ch.channel_url}</span>
          </li>
        ))}
      </ul>
      {selectedId && <ChannelDetail id={selectedId} />}
    </div>
  );
}
