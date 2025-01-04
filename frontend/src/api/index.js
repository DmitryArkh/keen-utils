export default class Api {
  static async getStatus() {
    return await this.get('/status');
  }

  static async get(endpoint, params = {}) {
    const url = new URL((import.meta.env.VITE_API_URL ?? (window.location.origin + '/api')) + endpoint);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    const response = await fetch(url);
    return this.#handleResponse(response);
  }

  static async post(endpoint, body = {}) {
    return this.#requestWithBody('POST', endpoint, body);
  }

  static async put(endpoint, body = {}) {
    return this.#requestWithBody('PUT', endpoint, body);
  }

  static async delete(endpoint, body = {}) {
    return this.#requestWithBody('DELETE', endpoint, body);
  }

  static async #requestWithBody(method, endpoint, body) {
    const response = await fetch((import.meta.env.VITE_API_URL ?? (window.location.origin + '/api')) + endpoint, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return this.#handleResponse(response);
  }

  static async #handleResponse(response) {
    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Ошибка: ${response.status} ${response.statusText} - ${errorMessage}`);
    }
    return response.json();
  }
}
