// services/api.ts

// Configuración de la URL base de la API
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

// Tipos para las respuestas de la API
export interface Caso {
  id: string;
  alerta: string;
  descripcion: string;
  dispositivo?: {
    user?: string;
    fecha?: string;
    hora?: string;
    nombrePolicia?: string;
    ubicacion?: string;
  };
}

export interface ChatBotResponse {
  respuesta: string;
  texto_ampliado?: string;
}

export interface DocumentoUploadResponse {
  estado: string;
  archivo: string;
  tipo_documento: string;
  fragmentos_cargados: number;
}

export interface NotificacionCaso {
  alerta: string;
  descripcion: string;
  user: string;
  fecha_hora: string;
  razon_sentencia: string;
  veredicto: string;
  lugar_reclusion: string;
  conclusion: string;
  fecha_creacion: string;
}

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Método genérico para hacer peticiones
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      console.log(`🌐 API Request: ${config.method || 'GET'} ${url}`);
      
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log(`✅ API Response: ${endpoint}`, data);
      
      return data;
    } catch (error) {
      console.error(`❌ API Error: ${endpoint}`, error);
      throw error;
    }
  }

  // === ENDPOINTS DE CASOS ===
  
  // Obtener todos los casos (MongoDB Alertas)
  async getCasos(): Promise<Caso[]> {
    return this.request<Caso[]>('/caso/');
  }

  // Crear un nuevo caso
  async crearCaso(caso: Omit<Caso, 'id'>): Promise<{ id: string }> {
    return this.request<{ id: string }>('/caso/', {
      method: 'POST',
      body: JSON.stringify(caso),
    });
  }

  // === ENDPOINTS DE CHATBOT ===
  
  // Obtener todos los casos disponibles para el chatbot
  async getCasosDisponibles(): Promise<{
    total_casos: number;
    casos: Array<{
      id: string;
      alerta: string;
      descripcion: string;
    }>;
  }> {
    return this.request('/chatbot/casos');
  }

  // Consultar chatbot con un caso específico
  async consultarChatbot(idCaso: string): Promise<ChatBotResponse> {
    return this.request<ChatBotResponse>(`/chatbot/chatcaso/${idCaso}`, {
      method: 'POST',
    });
  }

  // === ENDPOINTS DE DOCUMENTOS ===
  
  // Subir documento PDF o DOCX
  async subirDocumento(file: FormData): Promise<DocumentoUploadResponse> {
    return this.request<DocumentoUploadResponse>('/documento/subir', {
      method: 'POST',
      headers: {}, // Dejar que el navegador maneje el Content-Type para FormData
      body: file,
    });
  }

  // === ENDPOINTS DE NOTIFICACIONES ===
  
  // Obtener notificaciones de casos
  async getNotificaciones(): Promise<NotificacionCaso[]> {
    return this.request<NotificacionCaso[]>('/notificacionCaso');
  }

  // === MÉTODOS DE UTILIDAD ===
  
  // Verificar conectividad con la API
  async healthCheck(): Promise<{ status: string }> {
    try {
      // FastAPI por defecto expone /docs, usamos eso para verificar
      const response = await fetch(`${this.baseURL}/docs`);
      return { status: response.ok ? 'connected' : 'error' };
    } catch {
      return { status: 'disconnected' };
    }
  }

  // Obtener URL base actual
  getBaseURL(): string {
    return this.baseURL;
  }
}

// Exportar instancia singleton
export const apiService = new ApiService();
export default apiService;
