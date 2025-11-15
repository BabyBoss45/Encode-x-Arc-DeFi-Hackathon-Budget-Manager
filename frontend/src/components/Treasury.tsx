import { useEffect, useState } from 'react';
import { getTreasuryBalance, topUpTreasury, getTreasuryTransactions } from '../services/api';
import type { TreasuryTransaction } from '../types';
import { format } from 'date-fns';

function Treasury() {
  const [balance, setBalance] = useState<{ balance: number; balanceFormatted: string } | null>(null);
  const [transactions, setTransactions] = useState<TreasuryTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showTopUp, setShowTopUp] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [balanceData, transactionsData] = await Promise.all([
        getTreasuryBalance(),
        getTreasuryTransactions(),
      ]);
      setBalance(balanceData);
      setTransactions(transactionsData);
      setError(null);
    } catch (err) {
      setError('Failed to load treasury data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTopUp = async (e: React.FormEvent) => {
    e.preventDefault();
    const amount = parseFloat(topUpAmount);
    if (isNaN(amount) || amount <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);
      const result = await topUpTreasury(amount);
      setSuccess(result.message || 'Top-up initiated successfully');
      setTopUpAmount('');
      setShowTopUp(false);
      // Reload balance after a short delay
      setTimeout(() => {
        loadData();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to top up treasury');
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

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return <div className="loading">Loading treasury data...</div>;
  }

  return (
    <div>
      <h1 className="page-title">Treasury</h1>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
        <div className="stat-card" style={{ borderLeftColor: '#10b981' }}>
          <div className="stat-label">Current USDC Balance</div>
          <div className="stat-value positive">
            {balance ? balance.balanceFormatted : formatCurrency(balance?.balance || 0)}
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 className="card-title">Treasury Management</h2>
          <button
            className="btn btn-primary"
            onClick={() => setShowTopUp(!showTopUp)}
          >
            {showTopUp ? 'Cancel' : 'Top Up Treasury'}
          </button>
        </div>

        {showTopUp && (
          <form onSubmit={handleTopUp} style={{ marginBottom: '1.5rem', padding: '1rem', background: '#f9fafb', borderRadius: '8px' }}>
            <div className="form-group">
              <label className="form-label">Amount (USDC)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="form-input"
                value={topUpAmount}
                onChange={(e) => setTopUpAmount(e.target.value)}
                placeholder="Enter amount to top up"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Processing...' : 'Initiate Top-Up'}
            </button>
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              This will initiate the Circle payment flow to add funds to the treasury.
            </p>
          </form>
        )}
      </div>

      <div className="card">
        <h2 className="card-title">Transaction History</h2>
        {transactions.length === 0 ? (
          <p style={{ color: '#666', textAlign: 'center', padding: '2rem' }}>
            No transactions yet.
          </p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Amount</th>
                <th>Timestamp</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id}>
                  <td>
                    <span className={`badge ${tx.type === 'deposit' ? 'badge-active' : 'badge-inactive'}`}>
                      {tx.type === 'deposit' ? 'Deposit' : 'Payroll'}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600 }}>
                    {tx.type === 'deposit' ? '+' : '-'}
                    {formatCurrency(tx.amount)}
                  </td>
                  <td>{formatDate(tx.timestamp)}</td>
                  <td>{tx.description || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Treasury;

