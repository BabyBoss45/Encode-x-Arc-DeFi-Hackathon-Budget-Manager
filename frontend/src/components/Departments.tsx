import { useEffect, useState } from 'react';
import { getDepartments, createDepartment } from '../services/api';
import type { Department } from '../types';

function Departments() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '' });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    try {
      setLoading(true);
      const data = await getDepartments();
      setDepartments(data);
      setError(null);
    } catch (err) {
      setError('Failed to load departments');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setError('Department name is required');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      await createDepartment(formData.name.trim());
      setFormData({ name: '' });
      setShowForm(false);
      await loadDepartments();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create department');
    } finally {
      setSubmitting(false);
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
    return <div className="loading">Loading departments...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 className="page-title">Departments</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ Create Department'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {showForm && (
        <div className="card">
          <h2 className="card-title">Create Department</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Department Name</label>
              <input
                type="text"
                className="form-input"
                value={formData.name}
                onChange={(e) => setFormData({ name: e.target.value })}
                placeholder="Enter department name"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Creating...' : 'Create Department'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2 className="card-title">All Departments</h2>
        {departments.length === 0 ? (
          <p style={{ color: '#666', textAlign: 'center', padding: '2rem' }}>
            No departments yet. Create your first department above.
          </p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Number of Workers</th>
                <th>Total Monthly Payroll Cost</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {departments.map((dept) => (
                <tr key={dept.id}>
                  <td>{dept.name}</td>
                  <td>{dept.workerCount}</td>
                  <td>{formatCurrency(dept.totalMonthlyPayroll)}</td>
                  <td>
                    <span className={`badge ${dept.active ? 'badge-active' : 'badge-inactive'}`}>
                      {dept.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Departments;

