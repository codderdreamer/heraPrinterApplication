const API_BASE_URL = 'http://10.254.240.40:8088/api';
//const API_BASE_URL = 'http://127.0.0.1:8088/api';

export interface Printer {
  id: number;
  ip: string;
  name: string;
  dpi: number;
  width: number;
  height: number;
  is_online?: boolean;
  status?: string;
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
    return this.request<Printer>('/printer', {
      method: 'POST',
      body: JSON.stringify({ ip }),
    });
  }

  async createPrinter(printer: Omit<Printer, 'id'>): Promise<void> {
    return this.request<void>('/printers', {
      method: 'POST',
      body: JSON.stringify(printer),
    });
  }

  async updatePrinter(ip: string, printer: Omit<Printer, 'id'>): Promise<void> {
    return this.request<void>('/printer/update', {
      method: 'POST',
      body: JSON.stringify({ ...printer, ip }),
    });
  }

  async deletePrinter(ip: string): Promise<void> {
    return this.request<void>('/printer/delete', {
      method: 'POST',
      body: JSON.stringify({ ip }),
    });
  }

  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>('/health');
  }

  async getLogo(printerIp: string, settingsName: string = 'default'): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/printer/logo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ip: printerIp, name: settingsName }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.blob();
  }

  async getPrinterCount(): Promise<{ count: number }> {
    return this.request<{ count: number }>('/printers/count');
  }

  async printToPrinter(ip: string, printData: {
    type: 'bmp' | 'text';
    bmp_path?: string;
    text?: string;
    x?: number;
    y?: number;
  }): Promise<void> {
    return this.request<void>('/printer/print', {
      method: 'POST',
      body: JSON.stringify({ ip, ...printData }),
    });
  }

  async saveBitmapSettings(ip: string, name: string, settings: {
    textItems: any[];
    iconItems: any[];
    barcodeItems: any[];
  }): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/bitmap-settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ip,
        name,
        ...settings
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.blob();
  }

  async getBitmapSettings(ip: string, name?: string): Promise<{
    found: boolean;
    settings?: any;
    settings_list?: any[];
    name?: string;
    message?: string;
  }> {
    return this.request('/bitmap-settings/get', {
      method: 'POST',
      body: JSON.stringify({ ip, name }),
    });
  }

  async deleteBitmapSettings(ip: string, name: string): Promise<void> {
    return this.request<void>('/bitmap-settings/delete', {
      method: 'POST',
      body: JSON.stringify({ ip, name }),
    });
  }
}

export const apiService = new ApiService();
