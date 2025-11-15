import { useEffect, useState } from 'react';
import { getWorkers, addWorker, updateWorkerStatus, getDepartments } from '../services/api';
import type { Worker, Department } from '../types';

function Workers() {
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    departmentId: 0,
    wallet: '',
    salary: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [workersData, departmentsData] = await Promise.all([
        getWorkers(),
        getDepartments(),
      ]);
      setWorkers(workersData);
      setDepartments(departmentsData);
      setError(null);
    } catch (err) {
      setError('Failed to load data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.wallet.trim() || !formData.salary || formData.departmentId === 0) {
      setError('All fields are required');
      return;
    }

    const salary = parseFloat(formData.salary);
    if (isNaN(salary) || salary <= 0) {
      setError('Salary must be a positive number');
      return;
    }

    // Validate wallet address format (basic check)
    if (!formData.wallet.startsWith('0x') || formData.wallet.length !== 42) {
      setError('Invalid wallet address format (should be 0x followed by 40 hex characters)');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      await addWorker({
        name: formData.name.trim(),
        departmentId: formData.departmentId,
        wallet: formData.wallet.trim(),
        salary: salary * 1000000, // Convert to smallest unit (6 decimals for USDC)
      });
      setFormData({ name: '', departmentId: 0, wallet: '', salary: '' });
      setShowForm(false);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add worker');
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleStatus = async (workerId: number, currentStatus: boolean) => {
    try {
      await updateWorkerStatus(workerId, !currentStatus);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update worker status');
    }
  };

  const formatCurrency = (value: number) => {
    // Assuming value is in smallest unit (6 decimals)
    const usdValue = value / 1000000;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(usdValue);
  };

  const getDepartmentName = (departmentId: number) => {
    const dept = departments.find((d) => d.id === departmentId);
    return dept?.name || 'Unknown';
  };

  if (loading) {
    return <div className="loading">Loading workers...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 className="page-title">Workers</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ Add Worker'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {showForm && (
        <div className="card">
          <h2 className="card-title">Add Worker</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Name</label>
              <input
                type="text"
                className="form-input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter worker name"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Department</label>
              <select
                className="form-input"
                value={formData.departmentId}
                onChange={(e) => setFormData({ ...formData, departmentId: parseInt(e.target.value) })}
                required
              >
                <option value={0}>Select a department</option>
                {departments
                  .filter((d) => d.active)
                  .map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name}
                    </option>
                  ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Arc Wallet Address</label>
              <input
                type="text"
                className="form-input"
                value={formData.wallet}
                onChange={(e) => setFormData({ ...formData, wallet: e.target.value })}
                placeholder="0x..."
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Salary (USDC)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="form-input"
                value={formData.salary}
                onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
                placeholder="Enter monthly salary"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Adding...' : 'Add Worker'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2 className="card-title">All Workers</h2>
        {workers.length === 0 ? (
          <p style={{ color: '#666', textAlign: 'center', padding: '2rem' }}>
            No workers yet. Add your first worker above.
          </p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Department</th>
                <th>Salary</th>
                <th>Wallet Address</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {workers.map((worker) => (
                <tr key={worker.id}>
                  <td>{worker.name}</td>
                  <td>{getDepartmentName(worker.departmentId)}</td>
                  <td>{formatCurrency(worker.salary)}</td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                    {worker.wallet.slice(0, 10)}...{worker.wallet.slice(-8)}
                  </td>
                  <td>
                    <span className={`badge ${worker.active ? 'badge-active' : 'badge-inactive'}`}>
                      {worker.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <button
                      className={`btn ${worker.active ? 'btn-danger' : 'btn-success'}`}
                      style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                      onClick={() => handleToggleStatus(worker.id, worker.active)}
                    >
                      {worker.active ? 'Deactivate' : 'Activate'}
                    </button>
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

export default Workers;

