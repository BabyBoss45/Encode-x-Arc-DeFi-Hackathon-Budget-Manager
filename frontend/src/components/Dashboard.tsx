import { useEffect, useState } from 'react';
import { getDashboardStats } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { DashboardStats } from '../types';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await getDashboardStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard stats');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error || !stats) {
    return <div className="error">{error || 'No data available'}</div>;
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  return (
    <div className="dashboard">
      <h1 className="page-title">Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Treasury Balance</div>
          <div className="stat-value">{formatCurrency(stats.treasuryBalance)}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Revenue This Month</div>
          <div className="stat-value positive">{formatCurrency(stats.revenueThisMonth)}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Payroll This Month</div>
          <div className="stat-value negative">{formatCurrency(stats.payrollThisMonth)}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Profit</div>
          <div className={`stat-value ${stats.profit >= 0 ? 'positive' : 'negative'}`}>
            {formatCurrency(stats.profit)}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Margin</div>
          <div className={`stat-value ${stats.margin >= 0 ? 'positive' : 'negative'}`}>
            {stats.margin.toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Revenue vs Payroll Over Time</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={stats.revenueVsPayroll}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip formatter={(value: number) => formatCurrency(value)} />
            <Legend />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#10b981"
              strokeWidth={2}
              name="Revenue"
            />
            <Line
              type="monotone"
              dataKey="payroll"
              stroke="#ef4444"
              strokeWidth={2}
              name="Payroll"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Dashboard;

