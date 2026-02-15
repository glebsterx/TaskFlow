import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888';

interface Task {
  id: number;
  title: string;
  description?: string;
  assignee_name?: string;
  status: string;
  due_date?: string;
  created_at: string;
}

interface Stats {
  total: number;
  todo: number;
  doing: number;
  done: number;
  blocked: number;
}

interface TelegramUser {
  id: number;
  first_name: string;
  username?: string;
}

const Dashboard: React.FC = () => {
  const [filter, setFilter] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<TelegramUser | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      axios.get(`${API_URL}/api/me`, {
        headers: { Authorization: `Bearer ${storedToken}` }
      }).then(res => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('token');
          setToken(null);
        });
    }

    (window as any).onTelegramAuth = (user: any) => {
      axios.post(`${API_URL}/api/auth/telegram`, user)
        .then(res => {
          localStorage.setItem('token', res.data.access_token);
          setToken(res.data.access_token);
          setUser(res.data.user);
        })
        .catch(err => console.error('Auth failed:', err));
    };
  }, []);

  const { data: tasks, isLoading: tasksLoading } = useQuery<Task[]>({
    queryKey: ['tasks', filter],
    queryFn: async () => {
      if (!token) return [];
      const params = filter ? { status: filter } : {};
      const res = await axios.get(`${API_URL}/api/tasks`, {
        params,
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.data;
    },
    enabled: !!token,
  });

  const { data: stats } = useQuery<Stats>({
    queryKey: ['stats'],
    queryFn: async () => {
      if (!token) return null;
      const res = await axios.get(`${API_URL}/api/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.data;
    },
    enabled: !!token,
  });

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">TeamFlow</h1>
            <p className="text-gray-600">Войдите через Telegram</p>
          </div>
          <div className="flex justify-center">
            <script 
              async 
              src="https://telegram.org/js/telegram-widget.js?22"
              data-telegram-login="YOUR_BOT_USERNAME"
              data-size="large"
              data-onauth="onTelegramAuth(user)"
              data-request-access="write"
            ></script>
          </div>
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>🔒 Безопасный вход через Telegram</p>
          </div>
        </div>
      </div>
    );
  }

  const statusColors: Record<string, string> = {
    TODO: 'bg-gray-100 text-gray-800',
    DOING: 'bg-blue-100 text-blue-800',
    DONE: 'bg-green-100 text-green-800',
    BLOCKED: 'bg-red-100 text-red-800',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">TeamFlow</h1>
            <p className="text-gray-600">Доска задач команды</p>
          </div>
          {user && (
            <div className="flex items-center gap-2">
              <span className="text-gray-700">👤 {user.first_name}</span>
              <button
                onClick={() => {
                  localStorage.removeItem('token');
                  setToken(null);
                  setUser(null);
                }}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-sm"
              >
                Выйти
              </button>
            </div>
          )}
        </header>

        {stats && (
          <div className="grid grid-cols-5 gap-4 mb-8">
            {[
              { label: 'Всего', value: stats.total, bg: 'bg-white' },
              { label: 'TODO', value: stats.todo, bg: 'bg-gray-50' },
              { label: 'В работе', value: stats.doing, bg: 'bg-blue-50' },
              { label: 'Выполнено', value: stats.done, bg: 'bg-green-50' },
              { label: 'Заблокировано', value: stats.blocked, bg: 'bg-red-50' },
            ].map((stat, i) => (
              <div key={i} className={`${stat.bg} p-6 rounded-xl shadow-sm`}>
                <div className="text-3xl font-bold">{stat.value}</div>
                <div className="text-gray-600 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        )}

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setFilter(null)}
            className={`px-4 py-2 rounded-lg ${!filter ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
          >
            Все
          </button>
          {['TODO', 'DOING', 'DONE', 'BLOCKED'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg ${filter === status ? 'bg-blue-600 text-white' : 'bg-white'}`}
            >
              {status}
            </button>
          ))}
        </div>

        {tasksLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
            <p className="text-gray-500 mt-4">Загрузка...</p>
          </div>
        ) : tasks && tasks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tasks.map((task) => (
              <div key={task.id} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-lg">#{task.id} {task.title}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[task.status]}`}>
                    {task.status}
                  </span>
                </div>
                {task.description && (
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{task.description}</p>
                )}
                <div className="flex items-center justify-between text-sm">
                  {task.assignee_name && (
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs">
                      👤 {task.assignee_name}
                    </span>
                  )}
                  <span className="text-gray-500">
                    {new Date(task.created_at).toLocaleDateString('ru')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 bg-white rounded-xl">
            <div className="text-6xl mb-4">📋</div>
            <p className="text-gray-500">Создайте первую задачу через /task в Telegram</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
