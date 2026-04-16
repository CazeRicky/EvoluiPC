// API service for EvoluiPC backend integration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export interface User {
  username: string;
  email: string;
  token: string;
}

export interface MachineSnapshot {
  cpu: string;
  gpu: string;
  ram: string;
  motherboard: string;
  storage: string;
  psu: string;
  performance_score: number;
  compatibility_score: number;
}

export interface Diagnostic {
  id: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
  component: string;
}

export interface UpgradeStep {
  step: number;
  action: string;
  component: string;
  impact: string;
  impact_percentage: number;
  estimated_cost: number;
  priority: 'high' | 'medium' | 'low';
}

export interface CatalogItem {
  id: string;
  name: string;
  type: 'cpu' | 'gpu' | 'ram' | 'storage' | 'psu' | 'motherboard';
  price: number;
  source: string;
  affiliate_link: string;
  tag: string;
  compatibility: number;
  performance_gain: number;
  image?: string;
}

class ApiService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.getToken()) {
      headers.Authorization = `Token ${this.getToken()}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.clearToken();
        throw new Error('Unauthorized');
      }
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<User> {
    const data = await this.request<{ token: string; user: { username: string; email: string } }>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      }
    );

    this.setToken(data.token);
    return {
      username: data.user.username,
      email: data.user.email,
      token: data.token,
    };
  }

  async register(username: string, email: string, password: string): Promise<User> {
    const data = await this.request<{ token: string; user: { username: string; email: string } }>(
      '/auth/register',
      {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
      }
    );

    this.setToken(data.token);
    return {
      username: data.user.username,
      email: data.user.email,
      token: data.token,
    };
  }

  async getCurrentUser(): Promise<{ username: string; email: string }> {
    return this.request('/auth/me');
  }

  async logout(): Promise<void> {
    await this.request('/auth/logout', { method: 'POST' });
    this.clearToken();
  }

  // Data endpoints
  async getMachineData(): Promise<{ machine: MachineSnapshot; diagnostics: Diagnostic[] }> {
    return this.request('/machine/me');
  }

  async getUpgradeRoute(): Promise<{ route: UpgradeStep[] }> {
    return this.request('/upgrade-route/me');
  }

  async getCatalog(): Promise<{ catalog: CatalogItem[] }> {
    return this.request('/recommendations/me');
  }
}

export const apiService = new ApiService();