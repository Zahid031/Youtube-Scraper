import { useEffect, useState } from 'react';
import axios from 'axios';

export default function ChannelDetail({ id }) {
  const [channel, setChannel] = useState(null);

  useEffect(() => {
    axios.get(`/api/channels/${id}/`).then((res) => setChannel(res.data));
  }, [id]);

  if (!channel) return <div>Loading videos...</div>;

  return (
    <div>
      <h3>{channel.title} - Videos</h3>
      <ul>
        {channel.videos.map((video, i) => (
          <li key={i}>
            <a href={video.video_url} target="_blank" rel="noreferrer">{video.title}</a>
            <span> ({video.upload_date})</span>
            <span> - {video.duration} second</span>
            <span> - {video.view_count} views</span>
            <span> - {video.like_count} likes</span>
            <span> - {video.comment_count} comments</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
