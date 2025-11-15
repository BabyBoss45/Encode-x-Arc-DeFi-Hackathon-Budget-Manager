import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Departments from './components/Departments';
import Workers from './components/Workers';
import Treasury from './components/Treasury';
import Analytics from './components/Analytics';
import './App.css';

function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/departments', label: 'Departments', icon: '🏢' },
    { path: '/workers', label: 'Workers', icon: '👥' },
    { path: '/treasury', label: 'Treasury', icon: '💰' },
    { path: '/analytics', label: 'Analytics', icon: '📈' },
  ];

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <h1>BossBoard</h1>
      </div>
      <div className="nav-links">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={location.pathname === item.path ? 'nav-link active' : 'nav-link'}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/departments" element={<Departments />} />
            <Route path="/workers" element={<Workers />} />
            <Route path="/treasury" element={<Treasury />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

