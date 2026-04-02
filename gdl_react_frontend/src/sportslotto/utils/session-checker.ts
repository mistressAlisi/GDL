/**
 * Session Checker Utility
 * Helps debug Django session and authentication issues
 */

/**
 * Get a specific cookie by name
 */
export function getCookie(name: string): string | null {
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
 * Check if user has valid Django session
 */
export function hasValidSession(): boolean {
  const sessionId = getCookie('sessionid');
  const csrfToken = getCookie('csrftoken');

  return !!(sessionId && csrfToken);
}

/**
 * Get session status for debugging
 */
export function getSessionStatus(): {
  hasSession: boolean;
  hasCsrf: boolean;
  sessionId?: string;
  csrfToken?: string;
} {
  const sessionId = getCookie('sessionid');
  const csrfToken = getCookie('csrftoken');

  return {
    hasSession: !!sessionId,
    hasCsrf: !!csrfToken,
    sessionId: sessionId ? sessionId.substring(0, 10) + '...' : undefined,
    csrfToken: csrfToken ? csrfToken.substring(0, 10) + '...' : undefined,
  };
}

/**
 * Log detailed session information for debugging
 */
export function logSessionStatus(context: string = '') {
  const status = getSessionStatus();
  const prefix = context ? `[${context}] ` : '';

  console.log(`${prefix}🔐 Session Status:`, {
    hasSession: status.hasSession ? '✅' : '❌',
    hasCsrf: status.hasCsrf ? '✅' : '❌',
    sessionId: status.sessionId || 'missing',
    csrfToken: status.csrfToken || 'missing',
  });

  if (!status.hasSession) {
    console.warn(`${prefix}⚠️ No Django session found! User may need to login.`);
  }

  if (!status.hasCsrf) {
    console.warn(`${prefix}⚠️ No CSRF token found! Requests may fail.`);
  }

  return status;
}

/**
 * Wait for session to be established (useful after login)
 */
export async function waitForSession(maxAttempts: number = 5, delayMs: number = 200): Promise<boolean> {
  for (let i = 0; i < maxAttempts; i++) {
    if (hasValidSession()) {
      console.log(`✅ Session established after ${i + 1} attempt(s)`);
      return true;
    }

    console.log(`⏳ Waiting for session... attempt ${i + 1}/${maxAttempts}`);
    await new Promise(resolve => setTimeout(resolve, delayMs));
  }

  console.error('❌ Session not established after maximum attempts');
  return false;
}
