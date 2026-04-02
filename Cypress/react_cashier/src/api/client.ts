// API client with CSRF handling for Django backend

/**
 * Extract CSRF token from Django's csrftoken cookie
 */
export function getCsrfToken(): string | null {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : null;
}

/**
 * POST helper with CSRF token and session credentials
 */
export async function apiPost<T = unknown>(
  url: string,
  data: Record<string, string>
): Promise<T> {
  const csrftoken = getCsrfToken();
  const body = new URLSearchParams(data);
  if (csrftoken) {
    body.append("csrfmiddlewaretoken", csrftoken);
  }

  const res = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      ...(csrftoken && { "X-CSRFToken": csrftoken }),
    },
    body,
  });

  return res.json();
}

/**
 * GET helper with session credentials
 */
export async function apiGet<T = unknown>(url: string): Promise<T> {
  const res = await fetch(url, {
    method: "GET",
    credentials: "include",
  });

  return res.json();
}
