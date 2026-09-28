const AUTH_KEY = 'hidden_emotion_jwt_token';
const USER_KEY = 'hidden_emotion_user';

class AuthManager {
  constructor() {
    self.token = localStorage.getItem(AUTH_KEY) || null;
    self.user = JSON.parse(localStorage.getItem(USER_KEY) || 'null');
  }

  static getToken() {
    return localStorage.getItem(AUTH_KEY);
  }

  static getUser() {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null');
  }

  static setSession(token, user) {
    localStorage.setItem(AUTH_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  static clearSession() {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
  }

  static getAuthHeaders() {
    const token = AuthManager.getToken();
    if (token) {
      return { 'Authorization': `Bearer ${token}` };
    }
    return {};
  }

  static async login(email, password) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
      let errMsg = 'Login failed';
      try {
        const err = await response.json();
        errMsg = err.detail || errMsg;
      } catch (e) {
        errMsg = `Login error (${response.statusText || response.status})`;
      }
      throw new Error(errMsg);
    }
    
    const data = await response.json();
    AuthManager.setSession(data.access_token, data.user);
    return data.user;
  }

  static async register(username, email, password, role = 'user') {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password, role })
    });
    
    if (!response.ok) {
      let errMsg = 'Registration failed';
      try {
        const err = await response.json();
        errMsg = err.detail || errMsg;
      } catch (e) {
        errMsg = `Registration error (${response.statusText || response.status})`;
      }
      throw new Error(errMsg);
    }
    
    const data = await response.json();
    AuthManager.setSession(data.access_token, data.user);
    return data.user;
  }

  static logout() {
    AuthManager.clearSession();
    window.location.reload();
  }
}

window.AuthManager = AuthManager;
