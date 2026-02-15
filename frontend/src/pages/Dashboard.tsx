import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

const Dashboard: React.FC = () => {
  const [filter, setFilter] = useState<string | null>(null);

  const { data: tasks, isLoading: tasksLoading } = useQuery<Task[]>({
    queryKey: ['tasks', filter],
    queryFn: async () => {
      const params = filter ? { status: filter } : {};
      const res = await axios.get(`${API_URL}/api/tasks`, { params });
      return res.data;
    },
  });

  const { data: stats } = useQuery<Stats>({
    queryKey: ['stats'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/stats`);
      return res.data;
    },
  });

  const statusColors: Record<string, string> = {
    TODO: 'bg-gray-100 text-gray-800',
    DOING: 'bg-blue-100 text-blue-800',
    DONE: 'bg-green-100 text-green-800',
    BLOCKED: 'bg-red-100 text-red-800',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">TeamFlow</h1>
          <p className="text-gray-600">Доска задач команды (Read-Only)</p>
        </header>

        {stats && (
          <div className="grid grid-cols-5 gap-4 mb-8">
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-2xl font-bold">{stats.total}</div>
              <div className="text-gray-600">Всего</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg shadow">
              <div className="text-2xl font-bold">{stats.todo}</div>
              <div className="text-gray-600">TODO</div>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg shadow">
              <div className="text-2xl font-bold">{stats.doing}</div>
              <div className="text-gray-600">В работе</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg shadow">
              <div className="text-2xl font-bold">{stats.done}</div>
              <div className="text-gray-600">Выполнено</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg shadow">
              <div className="text-2xl font-bold">{stats.blocked}</div>
              <div className="text-gray-600">Заблокировано</div>
            </div>
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
              className={`px-4 py-2 rounded-lg ${filter === status ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
            >
              {status}
            </button>
          ))}
        </div>

        {tasksLoading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Загрузка задач...</p>
          </div>
        ) : tasks && tasks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tasks.map((task) => (
              <div key={task.id} className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-lg">#{task.id} {task.title}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[task.status]}`}>
                    {task.status}
                  </span>
                </div>
                {task.description && (
                  <p className="text-gray-600 text-sm mb-3">{task.description}</p>
                )}
                <div className="flex items-center justify-between text-sm text-gray-500">
                  {task.assignee_name && (
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                      {task.assignee_name}
                    </span>
                  )}
                  <span>{new Date(task.created_at).toLocaleDateString('ru')}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg">
            <p className="text-gray-500">Задач пока нет</p>
            <p className="text-gray-400 text-sm mt-2">Создайте первую задачу через Telegram бот командой /task</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
