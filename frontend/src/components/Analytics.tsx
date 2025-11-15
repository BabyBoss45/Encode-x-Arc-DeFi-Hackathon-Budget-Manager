import { useEffect, useState } from 'react';
import { getAnalytics } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import type { AnalyticsData } from '../types';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140'];

function Analytics() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await getAnalytics();
      setAnalytics(data);
      setError(null);
    } catch (err) {
      setError('Failed to load analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  if (error || !analytics) {
    return <div className="error">{error || 'No analytics data available'}</div>;
  }

  return (
    <div>
      <h1 className="page-title">Analytics</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Most Expensive Department</div>
          <div className="stat-value">{analytics.mostExpensiveDepartment}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Employees</div>
          <div className="stat-value">{analytics.totalEmployees}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Average Salary</div>
          <div className="stat-value">{formatCurrency(analytics.averageSalary)}</div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Spend per Department</h2>
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Pie
              data={analytics.spendPerDepartment}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={120}
              fill="#8884d8"
              dataKey="value"
            >
              {analytics.spendPerDepartment.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value: number) => formatCurrency(value)} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2 className="card-title">Payroll Trend Over Time</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={analytics.payrollTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip formatter={(value: number) => formatCurrency(value)} />
            <Legend />
            <Line
              type="monotone"
              dataKey="amount"
              stroke="#667eea"
              strokeWidth={2}
              name="Payroll"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2 className="card-title">Profit Over Time</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={analytics.profitTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip formatter={(value: number) => formatCurrency(value)} />
            <Legend />
            <Line
              type="monotone"
              dataKey="amount"
              stroke="#10b981"
              strokeWidth={2}
              name="Profit"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Analytics;

