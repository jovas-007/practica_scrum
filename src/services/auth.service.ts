import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

interface User {
  id_usuario: string;
  password: string;
  nombre_completo: string;
  correo: string;
  telefono: string;
  sexo: string;
  carrera: string;
  rol: 'docente' | 'estudiante';
}

interface LoginResponse {
  success: boolean;
  id_usuario?: string;
  nombre_completo?: string;
  correo?: string;
  rol?: 'docente' | 'estudiante';
  carrera?: string;
  message?: string;
}

interface RegisterResponse {
  success: boolean;
  message?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = 'http://localhost:3000/api';
  private readonly CURRENT_USER_KEY = 'currentUser';

  constructor(private http: HttpClient) {}

  async register(userData: {
    id_usuario: string;
    password: string;
    nombre_completo: string;
    correo: string;
    telefono: string;
    sexo: string;
    carrera: string;
    rol: string;
  }): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await firstValueFrom(
        this.http.post<RegisterResponse>(`${this.API_URL}/register`, userData)
      );
      return response;
    } catch (error: any) {
      // Si el servidor respondió con un error (400, 401, etc.), extraer el mensaje
      if (error.error && error.error.message) {
        return { success: false, message: error.error.message };
      }
      // Si es un error de conexión real
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  }

  async login(id_usuario: string, password: string): Promise<{ success: boolean; message?: string }> {
    try {
      // Limpiar localStorage antes del login
      localStorage.removeItem(this.CURRENT_USER_KEY);
      
      const response = await firstValueFrom(
        this.http.post<LoginResponse>(`${this.API_URL}/login`, { id_usuario, password })
      );

      if (response.success && response.id_usuario) {
        // Guardar datos del usuario incluyendo el rol que viene del backend
        const userData = {
          id_usuario: response.id_usuario,
          nombre_completo: response.nombre_completo,
          correo: response.correo || '',
          rol: response.rol || 'estudiante',
          carrera: response.carrera || ''
        };
        
        const userDataString = JSON.stringify(userData);
        console.log('=== GUARDANDO EN LOCALSTORAGE ===');
        console.log('User data object:', userData);
        console.log('User data string:', userDataString);
        
        localStorage.setItem(this.CURRENT_USER_KEY, userDataString);
        // Guardar también en cookie para compartir sesión entre puertos (4200 y 3000)
        document.cookie = `${this.CURRENT_USER_KEY}=${encodeURIComponent(userDataString)}; path=/; SameSite=Lax`;
        
        // Verificar que se guardó correctamente
        const saved = localStorage.getItem(this.CURRENT_USER_KEY);
        console.log('Verificación - localStorage guardado:', saved);
        console.log('Verificación - parseado:', JSON.parse(saved || '{}'));
        
        return { success: true };
      }
      
      return { success: false, message: 'Credenciales incorrectas' };
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  }

  logout(): void {
    localStorage.removeItem(this.CURRENT_USER_KEY);
    document.cookie = `${this.CURRENT_USER_KEY}=; Max-Age=0; path=/; SameSite=Lax`;
  }

  getCurrentUser(): { 
    id_usuario: string; 
    nombre_completo: string; 
    correo?: string; 
    rol?: 'docente' | 'estudiante';
    carrera?: string;
  } | null {
    const userData = localStorage.getItem(this.CURRENT_USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  isLoggedIn(): boolean {
    return this.getCurrentUser() !== null;
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.rol === 'docente';
  }

  isStudent(): boolean {
    const user = this.getCurrentUser();
    return user?.rol === 'estudiante';
  }

  async getAllUsers(): Promise<User[]> {
    try {
      return await firstValueFrom(
        this.http.get<User[]>(`${this.API_URL}/users`)
      );
    } catch (error) {
      return [];
    }
  }

  async recoverPassword(correo: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await firstValueFrom(
        this.http.post<{ success: boolean; message?: string }>(`${this.API_URL}/forgot-password`, { correo })
      );
      return response;
    } catch (error) {
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  }

  async sendRecoveryCode(correo: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await firstValueFrom(
        this.http.post<{ success: boolean; message?: string }>(`${this.API_URL}/forgot-password`, { correo })
      );
      return response;
    } catch (error) {
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  }

  async verifyRecoveryCode(correo: string, code: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await firstValueFrom(
        this.http.post<{ success: boolean; message?: string }>(`${this.API_URL}/verify-recovery-code`, { correo, code })
      );
      return response;
    } catch (error) {
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  }

  async resetPassword(correo: string, code: string, newPassword: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await firstValueFrom(
        this.http.post<{ success: boolean; message?: string }>(`${this.API_URL}/reset-password`, { correo, code, newPassword })
      );
      return response;
    } catch (error) {
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  }
}
