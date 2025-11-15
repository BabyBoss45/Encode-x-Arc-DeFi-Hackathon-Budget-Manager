export interface Department {
  id: number;
  name: string;
  active: boolean;
  workerCount: number;
  totalMonthlyPayroll: number;
}

export interface Worker {
  id: number;
  name: string;
  departmentId: number;
  departmentName?: string;
  wallet: string;
  salary: number;
  active: boolean;
}

export interface TreasuryBalance {
  balance: number;
  balanceFormatted: string;
}

export interface DashboardStats {
  treasuryBalance: number;
  revenueThisMonth: number;
  payrollThisMonth: number;
  profit: number;
  margin: number;
  revenueVsPayroll: Array<{ date: string; revenue: number; payroll: number }>;
}

export interface TreasuryTransaction {
  id: string;
  type: 'deposit' | 'payroll';
  amount: number;
  timestamp: string;
  description?: string;
}

export interface AnalyticsData {
  spendPerDepartment: Array<{ name: string; value: number }>;
  payrollTrend: Array<{ date: string; amount: number }>;
  profitTrend: Array<{ date: string; amount: number }>;
  mostExpensiveDepartment: string;
  totalEmployees: number;
  averageSalary: number;
}

