import { useEffect, useState } from 'react';
import axios from 'axios';

export default function TaskStatus({ trigger }) {
  const [tasks, setTasks] = useState([]);

  const fetchTasks = () => {
    axios.get('/api/tasks/')
      .then((res) => setTasks(res.data))
      .catch((err) => console.error('Error fetching tasks:', err));
  };

  useEffect(() => {
    fetchTasks(); // Fetch on mount or refresh
  }, [trigger]);

  useEffect(() => {
    const interval = setInterval(fetchTasks, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>Task Status</h2>
      <ul>
        {tasks.length === 0 && <li>No tasks yet</li>}
        {tasks.map((task) => (
          <li key={task.task_id}>
            <strong>{task.channel ? task.channel.title : 'Unknown Channel'}</strong> — 
            <span> {task.status.toUpperCase()}</span>
            {task.status === 'completed' && ` (${task.videos_scraped} videos)`}
            {task.status === 'failed' && (
              <span style={{ color: 'red' }}> ⚠ {task.error_message}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
