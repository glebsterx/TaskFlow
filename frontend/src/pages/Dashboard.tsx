import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8180';

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

// Declare global Telegram widget callback
declare global {
  interface Window {
    onTelegramAuth: (user: any) => void;
  }
}

const Dashboard: React.FC = () => {
  const [filter, setFilter] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [botUsername, setBotUsername] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetch bot info first (no auth required)
  useEffect(() => {
    console.log('Fetching bot info from:', `${API_URL}/api/bot-info`);
    
    axios.get(`${API_URL}/api/bot-info`)
      .then(res => {
        console.log('Bot info received:', res.data);
        setBotUsername(res.data.username);
        setError(null);
      })
      .catch(err => {
        console.error('Failed to load bot info:', err);
        console.error('Error details:', {
          message: err.message,
          response: err.response?.data,
          status: err.response?.status
        });
        setError(`Не удалось подключиться к боту: ${err.message}`);
      });
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      axios.get(`${API_URL}/api/me`, {
        headers: { Authorization: `Bearer ${storedToken}` }
      }).then(res => {
        setUser(res.data);
        setIsLoading(false);
      }).catch(() => {
        localStorage.removeItem('token');
        setToken(null);
        setIsLoading(false);
      });
    } else {
      setIsLoading(false);
    }

    // Setup Telegram auth callback
    window.onTelegramAuth = (user: any) => {
      console.log('Telegram auth callback triggered:', user);
      axios.post(`${API_URL}/api/auth/telegram`, user)
        .then(res => {
          console.log('Auth successful:', res.data);
          localStorage.setItem('token', res.data.access_token);
          setToken(res.data.access_token);
          setUser(res.data.user);
        })
        .catch(err => {
          console.error('Auth failed:', err);
          alert('Ошибка авторизации. Проверьте настройки бота.');
        });
    };
  }, []);

  // Load Telegram Widget when bot username is available
  useEffect(() => {
    if (!token && botUsername && !document.getElementById('telegram-widget-script')) {
      console.log('Loading Telegram widget for bot:', botUsername);
      
      const script = document.createElement('script');
      script.id = 'telegram-widget-script';
      script.src = 'https://telegram.org/js/telegram-widget.js?22';
      script.setAttribute('data-telegram-login', botUsername);
      script.setAttribute('data-size', 'large');
      script.setAttribute('data-onauth', 'onTelegramAuth(user)');
      script.setAttribute('data-request-access', 'write');
      script.async = true;
      
      const container = document.getElementById('telegram-login-container');
      if (container) {
        container.appendChild(script);
      }
    }
  }, [token, botUsername]);

  const { data: tasks, isLoading: tasksLoading, refetch: refetchTasks } = useQuery<Task[]>({
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
    refetchInterval: 5000,
  });

  const { data: stats, refetch: refetchStats } = useQuery<Stats>({
    queryKey: ['stats'],
    queryFn: async () => {
      if (!token) return null;
      const res = await axios.get(`${API_URL}/api/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.data;
    },
    enabled: !!token,
    refetchInterval: 5000,
  });

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">❌</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Ошибка подключения</h1>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-red-800">{error}</p>
          </div>

          <div className="space-y-2 text-sm text-gray-600">
            <p><strong>Проверьте:</strong></p>
            <ul className="list-disc list-inside space-y-1">
              <li>Backend запущен на {API_URL}</li>
              <li>CORS настроен правильно</li>
              <li>TELEGRAM_BOT_USERNAME в .env</li>
            </ul>
          </div>

          <button
            onClick={() => window.location.reload()}
            className="mt-6 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            🔄 Попробовать снова
          </button>

          <div className="mt-4 text-xs text-gray-400 text-center">
            <p>API URL: {API_URL}</p>
            <p>Откройте консоль браузера (F12) для деталей</p>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading || !botUsername) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">
            {!botUsername ? 'Подключение к боту...' : 'Загрузка...'}
          </p>
          <p className="text-xs text-gray-400 mt-2">
            API: {API_URL}
          </p>
        </div>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">📋</div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">TeamFlow</h1>
            <p className="text-gray-600">Управление задачами команды</p>
          </div>
          
          <div className="mb-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-green-800 font-medium flex items-center">
                <span className="mr-2">✅</span>
                Подключено к боту
              </p>
              <p className="text-xs text-green-600 mt-1">
                @{botUsername}
              </p>
            </div>
          </div>

          <div id="telegram-login-container" className="flex justify-center mb-6 min-h-[60px]">
            {!document.getElementById('telegram-widget-script') && (
              <p className="text-sm text-gray-500">Загрузка кнопки авторизации...</p>
            )}
          </div>

          <div className="text-center text-sm text-gray-500 space-y-2">
            <p>🔒 Безопасный вход через Telegram</p>
            <p>Только члены команды имеют доступ</p>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-400 text-center">
              TeamFlow v0.3.1
            </p>
          </div>
        </div>
      </div>
    );
  }

  const statusColors: Record<string, string> = {
    TODO: 'bg-gray-100 text-gray-800 border-gray-300',
    DOING: 'bg-blue-100 text-blue-800 border-blue-300',
    DONE: 'bg-green-100 text-green-800 border-green-300',
    BLOCKED: 'bg-red-100 text-red-800 border-red-300',
  };

  const statusEmoji: Record<string, string> = {
    TODO: '📝',
    DOING: '🔄',
    DONE: '✅',
    BLOCKED: '🚫',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">TeamFlow</h1>
            <p className="text-gray-600">Доска задач команды</p>
          </div>
          {user && (
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-500">Вы вошли как</p>
                <p className="font-medium">👤 {user.first_name}</p>
              </div>
              <button
                onClick={() => {
                  localStorage.removeItem('token');
                  setToken(null);
                  setUser(null);
                  window.location.reload();
                }}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-sm transition"
              >
                Выйти
              </button>
            </div>
          )}
        </header>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-5 gap-4 mb-8">
            {[
              { label: 'Всего', value: stats.total, bg: 'bg-white', border: 'border-gray-200' },
              { label: 'TODO', value: stats.todo, bg: 'bg-gray-50', border: 'border-gray-300' },
              { label: 'В работе', value: stats.doing, bg: 'bg-blue-50', border: 'border-blue-200' },
              { label: 'Выполнено', value: stats.done, bg: 'bg-green-50', border: 'border-green-200' },
              { label: 'Заблокировано', value: stats.blocked, bg: 'bg-red-50', border: 'border-red-200' },
            ].map((stat, i) => (
              <div key={i} className={`${stat.bg} p-6 rounded-xl shadow-sm border ${stat.border}`}>
                <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-gray-600 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Filters */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setFilter(null)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              !filter 
                ? 'bg-blue-600 text-white shadow-md' 
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            }`}
          >
            Все
          </button>
          {['TODO', 'DOING', 'DONE', 'BLOCKED'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === status 
                  ? 'bg-blue-600 text-white shadow-md' 
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
              }`}
            >
              {statusEmoji[status]} {status}
            </button>
          ))}
        </div>

        {/* Tasks */}
        {tasksLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-500">Загрузка задач...</p>
          </div>
        ) : tasks && tasks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tasks.map((task) => (
              <div 
                key={task.id} 
                className="bg-white p-6 rounded-xl shadow-sm border-2 hover:shadow-md transition-all cursor-pointer"
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-lg text-gray-900">
                    #{task.id} {task.title}
                  </h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border-2 ${statusColors[task.status]}`}>
                    {statusEmoji[task.status]} {task.status}
                  </span>
                </div>
                {task.description && (
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{task.description}</p>
                )}
                <div className="flex items-center justify-between text-sm">
                  {task.assignee_name && (
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium">
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
          <div className="text-center py-16 bg-white rounded-xl shadow-sm">
            <div className="text-6xl mb-4">📋</div>
            <p className="text-gray-500 text-lg mb-2">Задач пока нет</p>
            <p className="text-gray-400 text-sm mb-4">
              Создайте первую задачу через Telegram бот командой <code className="bg-gray-100 px-2 py-1 rounded">/task</code>
            </p>
            <button
              onClick={() => {
                refetchTasks();
                refetchStats();
              }}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              🔄 Обновить
            </button>
          </div>
        )}

        {/* Auto-refresh indicator */}
        <div className="fixed bottom-4 right-4 bg-white px-4 py-2 rounded-lg shadow-lg border border-gray-200">
          <p className="text-xs text-gray-500 flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            Автообновление каждые 5 сек
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
