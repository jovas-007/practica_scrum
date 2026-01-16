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
}

interface LoginResponse {
  success: boolean;
  id_usuario?: string;
  nombre_completo?: string;
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
  }): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await firstValueFrom(
        this.http.post<RegisterResponse>(`${this.API_URL}/register`, userData)
      );
      return response;
    } catch (error) {
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  }

  async login(id_usuario: string, password: string): Promise<boolean> {
    try {
      const response = await firstValueFrom(
        this.http.post<LoginResponse>(`${this.API_URL}/login`, { id_usuario, password })
      );

      if (response.success && response.id_usuario) {
        const userData = JSON.stringify({
          id_usuario: response.id_usuario,
          nombre_completo: response.nombre_completo
        });
        localStorage.setItem(this.CURRENT_USER_KEY, userData);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error de conexión:', error);
      return false;
    }
  }

  logout(): void {
    localStorage.removeItem(this.CURRENT_USER_KEY);
  }

  getCurrentUser(): { id_usuario: string; nombre_completo: string } | null {
    const userData = localStorage.getItem(this.CURRENT_USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  isLoggedIn(): boolean {
    return this.getCurrentUser() !== null;
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
}
