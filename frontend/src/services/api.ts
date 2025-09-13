const API_BASE_URL = 'http://localhost:8080/api';

export interface Printer {
  id: number;
  ip: string;
  name: string;
  dpi: number;
  width: number;
  height: number;
}

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getPrinters(): Promise<Printer[]> {
    return this.request<Printer[]>('/printers');
  }

  async getPrinter(ip: string): Promise<Printer> {
    return this.request<Printer>(`/printers/${ip}`);
  }

  async createPrinter(printer: Omit<Printer, 'id'>): Promise<void> {
    return this.request<void>('/printers', {
      method: 'POST',
      body: JSON.stringify(printer),
    });
  }

  async updatePrinter(ip: string, printer: Omit<Printer, 'id'>): Promise<void> {
    return this.request<void>(`/printers/${ip}`, {
      method: 'PUT',
      body: JSON.stringify(printer),
    });
  }

  async deletePrinter(ip: string): Promise<void> {
    return this.request<void>(`/printers/${ip}`, {
      method: 'DELETE',
    });
  }

  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>('/health');
  }

  async saveBitmapSettings(settings: any): Promise<void> {
    return this.request<void>('/bitmap-settings', {
      method: 'POST',
      body: JSON.stringify(settings),
    });
  }
}

export const apiService = new ApiService();
