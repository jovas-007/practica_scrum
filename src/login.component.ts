import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="auth-container">
      <div class="auth-card">
        <h2>Iniciar Sesión</h2>
        
        <form (ngSubmit)="login()" *ngIf="!showRegister">
          <div class="form-group">
            <label>Matrícula:</label>
            <input 
              type="text" 
              [(ngModel)]="id_usuario" 
              name="id_usuario"
              placeholder="Ingrese su matrícula"
              required>
          </div>
          
          <div class="form-group">
            <label>Contraseña:</label>
            <input 
              type="password" 
              [(ngModel)]="password" 
              name="password"
              placeholder="Ingrese su contraseña"
              required>
          </div>
          
          <div class="message" [class.error]="errorMessage">
            {{ errorMessage || successMessage }}
          </div>
          
          <button type="submit" class="btn-primary">Ingresar</button>
          <button type="button" class="btn-secondary" (click)="showRegister = true">
            Crear cuenta nueva
          </button>
        </form>

        <form (ngSubmit)="register()" *ngIf="showRegister">
          <div class="form-group">
            <label>Matrícula:</label>
            <input 
              type="text" 
              [(ngModel)]="newUser.id_usuario" 
              name="id_usuario"
              placeholder="9 dígitos"
              pattern="[0-9]{9}"
              maxlength="9"
              required>
          </div>
          
          <div class="form-group">
            <label>Nombre Completo:</label>
            <input 
              type="text" 
              [(ngModel)]="newUser.nombre_completo" 
              name="nombre_completo"
              placeholder="Nombre completo"
              required>
          </div>

          <div class="form-group">
            <label>Correo:</label>
            <input 
              type="email" 
              [(ngModel)]="newUser.correo" 
              name="correo"
              placeholder="correo@ejemplo.com"
              required>
          </div>

          <div class="form-group">
            <label>Teléfono:</label>
            <input 
              type="tel" 
              [(ngModel)]="newUser.telefono" 
              name="telefono"
              placeholder="10 dígitos"
              pattern="[0-9]{10}"
              maxlength="10"
              required>
          </div>

          <div class="form-group">
            <label>Sexo:</label>
            <select [(ngModel)]="newUser.sexo" name="sexo" required>
              <option value="">Seleccione...</option>
              <option value="Masculino">Masculino</option>
              <option value="Femenino">Femenino</option>
              <option value="Otro">Otro</option>
            </select>
          </div>

          <div class="form-group">
            <label>Carrera:</label>
            <input 
              type="text" 
              [(ngModel)]="newUser.carrera" 
              name="carrera"
              placeholder="Nombre de la carrera"
              required>
          </div>
          
          <div class="form-group">
            <label>Contraseña:</label>
            <input 
              type="password" 
              [(ngModel)]="newUser.password" 
              name="password"
              placeholder="8-15 caracteres alfanuméricos"
              minlength="8"
              maxlength="15"
              pattern="[a-zA-Z0-9]+"
              required>
          </div>

          <div class="form-group">
            <label>Confirmar Contraseña:</label>
            <input 
              type="password" 
              [(ngModel)]="confirmPassword" 
              name="confirmPassword"
              placeholder="Confirme su contraseña"
              required>
          </div>
          
          <div class="message" [class.error]="errorMessage">
            {{ errorMessage || successMessage }}
          </div>
          
          <button type="submit" class="btn-primary">Registrar</button>
          <button type="button" class="btn-secondary" (click)="backToLogin()">
            Volver al inicio de sesión
          </button>
        </form>

        <div class="logged-in" *ngIf="isLoggedIn">
          <h3>¡Bienvenido, {{ currentUser }}!</h3>
          <p>Has iniciado sesión correctamente.</p>
          <button class="btn-primary" (click)="logout()">Cerrar Sesión</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .auth-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: #f4f7f9;
      padding: 20px;
    }

    .auth-card {
      background: white;
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      width: 100%;
      max-width: 400px;
    }

    h2 {
      text-align: center;
      color: #003b5c;
      margin-bottom: 30px;
    }

    h3 {
      color: #059669;
      text-align: center;
    }

    .form-group {
      margin-bottom: 20px;
    }

    label {
      display: block;
      margin-bottom: 8px;
      color: #475569;
      font-weight: 600;
    }

    input {
      width: 100%;
      padding: 12px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font-size: 14px;
      box-sizing: border-box;
    }

    select {
      width: 100%;
      padding: 12px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font-size: 14px;
      box-sizing: border-box;
      background: white;
    }

    input:focus, select:focus {
      outline: none;
      border-color: #2563eb;
    }

    .message {
      padding: 10px;
      border-radius: 6px;
      margin-bottom: 15px;
      text-align: center;
      background: #d1fae5;
      color: #059669;
    }

    .message.error {
      background: #fee2e2;
      color: #dc2626;
    }

    .message:empty {
      display: none;
    }

    button {
      width: 100%;
      padding: 12px;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      margin-bottom: 10px;
      transition: all 0.2s;
    }

    .btn-primary {
      background: #003b5c;
      color: white;
    }

    .btn-primary:hover {
      background: #2563eb;
    }

    .btn-secondary {
      background: #f1f5f9;
      color: #475569;
      border: 1px solid #cbd5e1;
    }

    .btn-secondary:hover {
      background: #e2e8f0;
    }

    .logged-in {
      text-align: center;
    }

    .logged-in p {
      color: #64748b;
      margin-bottom: 20px;
    }
  `]
})
export class LoginComponent {
  id_usuario = '';
  password = '';
  newUser = {
    id_usuario: '',
    password: '',
    nombre_completo: '',
    correo: '',
    telefono: '',
    sexo: '',
    carrera: ''
  };
  confirmPassword = '';
  errorMessage = '';
  successMessage = '';
  showRegister = false;
  isLoggedIn = false;
  currentUser = '';

  constructor(private authService: AuthService) {
    // Verificar sesión después de que el componente esté listo
    setTimeout(() => this.checkLoginStatus(), 0);
  }

  checkLoginStatus() {
    try {
      const user = this.authService.getCurrentUser();
      if (user) {
        this.isLoggedIn = true;
        this.currentUser = user.nombre_completo;
      }
    } catch (error) {
      console.error('Error checking login status:', error);
    }
  }

  async login() {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.id_usuario || !this.password) {
      this.errorMessage = 'Por favor complete todos los campos';
      return;
    }

    const success = await this.authService.login(this.id_usuario, this.password);
    
    if (success) {
      this.successMessage = '¡Inicio de sesión exitoso! Redirigiendo...';
      setTimeout(() => {
        window.location.href = 'pantalla_inicio.html';
      }, 1000);
    } else {
      this.errorMessage = 'Matrícula o contraseña incorrectos';
    }
  }

  async register() {
    this.errorMessage = '';
    this.successMessage = '';

    // Validación: todos los campos completos
    if (!this.newUser.id_usuario || !this.newUser.password || !this.confirmPassword ||
        !this.newUser.nombre_completo || !this.newUser.correo || !this.newUser.telefono ||
        !this.newUser.sexo || !this.newUser.carrera) {
      this.errorMessage = 'Por favor complete todos los campos';
      return;
    }

    // Validación: matrícula de exactamente 9 dígitos
    if (!/^\d{9}$/.test(this.newUser.id_usuario)) {
      this.errorMessage = 'La matrícula debe tener exactamente 9 dígitos';
      return;
    }

    // Validación: correo electrónico válido
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.newUser.correo)) {
      this.errorMessage = 'Por favor ingrese un correo electrónico válido';
      return;
    }

    // Validación: teléfono de exactamente 10 dígitos
    if (!/^\d{10}$/.test(this.newUser.telefono)) {
      this.errorMessage = 'El teléfono debe tener exactamente 10 dígitos';
      return;
    }

    // Validación: contraseña mínimo 8 y máximo 15 caracteres
    if (this.newUser.password.length < 8 || this.newUser.password.length > 15) {
      this.errorMessage = 'La contraseña debe tener entre 8 y 15 caracteres';
      return;
    }

    // Validación: contraseña alfanumérica
    if (!/^[a-zA-Z0-9]+$/.test(this.newUser.password)) {
      this.errorMessage = 'La contraseña debe ser alfanumérica (solo letras y números)';
      return;
    }

    // Validación: confirmar contraseña
    if (this.newUser.password !== this.confirmPassword) {
      this.errorMessage = 'Las contraseñas no coinciden';
      return;
    }

    const result = await this.authService.register(this.newUser);
    
    if (result.success) {
      this.successMessage = '¡Usuario registrado exitosamente!';
      setTimeout(() => {
        this.backToLogin();
      }, 1500);
    } else {
      this.errorMessage = result.message || 'Error al registrar usuario';
    }
  }

  backToLogin() {
    this.showRegister = false;
    this.newUser = {
      id_usuario: '',
      password: '',
      nombre_completo: '',
      correo: '',
      telefono: '',
      sexo: '',
      carrera: ''
    };
    this.confirmPassword = '';
    this.errorMessage = '';
    this.successMessage = '';
  }

  logout() {
    this.authService.logout();
    this.isLoggedIn = false;
    this.currentUser = '';
    this.successMessage = 'Sesión cerrada correctamente';
    setTimeout(() => {
      this.successMessage = '';
    }, 2000);
  }
}
