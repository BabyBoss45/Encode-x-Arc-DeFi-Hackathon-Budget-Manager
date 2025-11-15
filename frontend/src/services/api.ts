import axios from 'axios';
import type { Department, Worker, DashboardStats, TreasuryTransaction, AnalyticsData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get('/dashboard/stats');
  return response.data;
};

// Treasury
export const getTreasuryBalance = async (): Promise<{ balance: number; balanceFormatted: string }> => {
  const response = await api.get('/treasury/balance');
  return response.data;
};

export const topUpTreasury = async (amount: number): Promise<{ success: boolean; message: string }> => {
  const response = await api.post('/treasury/top-up', { amount });
  return response.data;
};

export const getTreasuryTransactions = async (): Promise<TreasuryTransaction[]> => {
  const response = await api.get('/treasury/transactions');
  return response.data;
};

// Departments
export const getDepartments = async (): Promise<Department[]> => {
  const response = await api.get('/departments');
  return response.data;
};

export const createDepartment = async (name: string): Promise<Department> => {
  const response = await api.post('/departments', { name });
  return response.data;
};

// Workers
export const getWorkers = async (): Promise<Worker[]> => {
  const response = await api.get('/workers');
  return response.data;
};

export const addWorker = async (data: {
  name: string;
  departmentId: number;
  wallet: string;
  salary: number;
}): Promise<Worker> => {
  const response = await api.post('/workers', data);
  return response.data;
};

export const updateWorkerStatus = async (workerId: number, active: boolean): Promise<Worker> => {
  const response = await api.patch(`/workers/${workerId}/status`, { active });
  return response.data;
};

// Analytics
export const getAnalytics = async (): Promise<AnalyticsData> => {
  const response = await api.get('/analytics');
  return response.data;
};

export default api;

