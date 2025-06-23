// File: src/App.jsx
import ChannelForm from './components/ChannelForm';
import ChannelList from './components/ChannelList';
import TaskStatus from './components/TaskStatus';
import { useState } from 'react';

export default function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(false);

  const refresh = () => {
    setRefreshTrigger(prev => !prev);
  };

  return (
    <div>
      <h1>YouTube Channel Scraper</h1>
      <ChannelForm onSuccess={refresh} />
      <TaskStatus trigger={refreshTrigger} />
      <ChannelList trigger={refreshTrigger} />
    </div>
  );
}