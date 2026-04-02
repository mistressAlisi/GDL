/**
 * CSRF Utility for Django Integration
 * Provides reusable CSRF token handling for all API requests
 */

/**
 * Retrieves CSRF token from Django's csrftoken cookie
 */
export function getCsrfToken(): string | null {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Custom fetch wrapper that automatically includes CSRF token and credentials
 * Use this for all POST, PUT, PATCH, DELETE requests to Django backend
 */
export async function csrfFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const csrfToken = getCsrfToken();

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...(csrfToken && { 'X-CSRFToken': csrfToken }),
  };

  const mergedOptions: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
    credentials: 'include', // Always include cookies for Django session
  };

  return fetch(url, mergedOptions);
}

/**
 * POST request with CSRF token
 */
export async function csrfPost<T = any>(url: string, data?: any): Promise<T> {
  const response = await csrfFetch(url, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(errorData.error || errorData.message || `HTTP error ${response.status}`);
  }

  return response.json();
}

/**
 * PUT request with CSRF token
 */
export async function csrfPut<T = any>(url: string, data?: any): Promise<T> {
  const response = await csrfFetch(url, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(errorData.error || errorData.message || `HTTP error ${response.status}`);
  }

  return response.json();
}

/**
 * PATCH request with CSRF token
 */
export async function csrfPatch<T = any>(url: string, data?: any): Promise<T> {
  const response = await csrfFetch(url, {
    method: 'PATCH',
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(errorData.error || errorData.message || `HTTP error ${response.status}`);
  }

  return response.json();
}

/**
 * DELETE request with CSRF token
 */
export async function csrfDelete<T = any>(url: string): Promise<T> {
  const response = await csrfFetch(url, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(errorData.error || errorData.message || `HTTP error ${response.status}`);
  }

  // Handle 204 No Content responses
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

/**
 * GET request with credentials (for authenticated endpoints)
 */
export async function csrfGet<T = any>(url: string): Promise<T> {
  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(errorData.error || errorData.message || `HTTP error ${response.status}`);
  }

  return response.json();
}
