/**
 * API Service for REST API Integration
 * Handles ticket acceptance, rejection, and cart management
 */

import { logSessionStatus } from '../utils/session-checker';

// Get CSRF token from cookie
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

// Get session ID - check multiple possible cookie names
function getSessionId(): string | null {
  // Django can use different session cookie names
  const possibleNames = ['sessionid', 'django_session', 'session'];

  for (const name of possibleNames) {
    const value = getCookie(name);
    if (value) {
      console.log(`✅ Found session cookie: ${name}`);
      return value;
    }
  }

  console.warn('⚠️ No session cookie found. Tried:', possibleNames);
  return null;
}

// Debug: Log all cookies
function debugCookies() {
  console.log('🍪 All cookies:', document.cookie);
  console.log('🍪 CSRF token:', getCookie('csrftoken'));
  console.log('🍪 Session ID (sessionid):', getCookie('sessionid'));
  console.log('🍪 Session ID (django_session):', getCookie('django_session'));
  console.log('🍪 Session ID (session):', getCookie('session'));

  // List all cookie names
  const allCookies = document.cookie.split(';').map(c => c.trim().split('=')[0]);
  console.log('🍪 All cookie names:', allCookies);
}

// Get API prefix from current URL path (e.g., /solstic.gdl/play/custom -> /api/v1/solstic.gdl/)
function getApiPrefix(): string {
  const pathParts = window.location.pathname.split('/').filter(p => p);
  if (pathParts.length > 0) {
    return `/api/v1/${pathParts[0]}/`;
  }
  return '/api/v1/';
}

// Base API configuration
const API_PREFIX = getApiPrefix();

export interface ApiResponse<T = any> {
  res: 'ok' | 'error';
  data?: T;
  err?: string;
  msg?: string;
  header?: string;
  silent?: boolean;
}

export interface AcceptTicketResponse {
  uuid: string;
  status: string;
  cart_count: number;
  available: number;
  balance: number;
  pending: number;
  bonus: number;
}

export interface RejectTicketResponse {
  status: string;
  cart_count: number;
}

export interface CartTicket {
  uuid: string;
  risk: number;
  returns: number;
  events: number;
  legs: any[];
  status: string;
  depth: number;
}

export interface CartResponse {
  count: number;
  tickets: CartTicket[];
  total_risk: number;
  total_wins: number;
}

export interface TicketData {
  uuid: string;
  muuids: string[];      // match UUIDs
  outcomes: string[];    // bet types (e.g., "home", "away", "over")
  lines: string[];       // line values
  stake: number;
  returns: number;
  outcome_meta: any;     // metadata for outcomes
  depth: number;         // number of events
  // Django session tracking
  vhost?: string;
  vdomain?: string;
  account?: string;
}

/**
 * Generic POST request with CSRF token and session handling
 */
async function apiPost<T = any>(url: string, data?: FormData | Record<string, any>): Promise<ApiResponse<T>> {
  const csrfToken = getCookie('csrftoken');
  const sessionId = getSessionId();

  // Log session info for debugging
  console.log('🔐 API POST Session Info:', {
    url,
    hasCSRF: !!csrfToken,
    hasSession: !!sessionId,
    csrfToken: csrfToken ? csrfToken.substring(0, 10) + '...' : 'missing',
    sessionId: sessionId ? sessionId.substring(0, 10) + '...' : 'missing',
  });

  // Use logSessionStatus for detailed logging
  logSessionStatus('API POST');

  if (!csrfToken) {
    console.error('❌ Missing CSRF token! Request will fail.');
    console.error('❌ Check that Django is setting csrftoken cookie properly.');
    debugCookies(); // Show all cookies for debugging
    return {
      res: 'error',
      err: 'Missing CSRF token. Please refresh the page and try again.',
    };
  }

  if (!sessionId) {
    console.warn('⚠️ Missing session ID! This might be expected if Django handles auth differently.');
    console.warn('⚠️ Proceeding with request - Django will return an error if authentication is required.');
    debugCookies(); // Show all cookies for debugging
    // Don't return error - let Django handle it
  }

  let body: FormData | string;
  const headers: HeadersInit = {
    'X-CSRFToken': csrfToken,
    'X-Requested-With': 'XMLHttpRequest', // Indicate AJAX request to Django
  };

  if (data instanceof FormData) {
    body = data;
    // Don't set Content-Type for FormData - browser will set it with boundary
  } else {
    body = JSON.stringify(data || {});
    headers['Content-Type'] = 'application/json';
  }

  try {
    console.log('📡 Making POST request to:', url);
    console.log('📡 Headers:', headers);
    console.log('📡 Body:', data instanceof FormData ? '[FormData]' : data);

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body,
      credentials: 'include', // CRITICAL: Include cookies (session + CSRF)
      mode: 'cors', // Enable CORS
    });

    console.log('📥 Response status:', response.status, response.statusText);

    if (!response.ok) {
      console.error('❌ HTTP error:', response.status, response.statusText);
      // Try to get error details from response
      const errorText = await response.text();
      console.error('❌ Error response:', errorText);

      // Check for common Django errors
      if (response.status === 403) {
        return {
          res: 'error',
          err: 'CSRF verification failed. Please refresh the page and try again.',
        };
      } else if (response.status === 401) {
        // Session expired - show message and redirect to login
        alert('Session Expired\n\nYour session has expired. Please log in again.');

        // Clear any stored user data
        localStorage.removeItem('sportslotto_user');

        // Redirect to login page
        window.location.href = '/';

        return {
          res: 'error',
          err: 'Authentication required. Please log in.',
        };
      }

      return {
        res: 'error',
        err: `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    const result = await response.json();
    console.log('✅ Response data:', result);
    return result;
  } catch (error) {
    console.error('❌ API POST error:', error);
    return {
      res: 'error',
      err: error instanceof Error ? error.message : 'Network error',
    };
  }
}

/**
 * Generic GET request
 */
async function apiGet<T = any>(url: string): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
    });

    console.log('📥 GET Response status:', response.status, response.statusText);

    if (!response.ok) {
      console.error('❌ HTTP error:', response.status, response.statusText);

      // Check for session expiration (401)
      if (response.status === 401) {
        // Session expired - show message and redirect to login
        alert('Session Expired\n\nYour session has expired. Please log in again.');

        // Clear any stored user data
        localStorage.removeItem('sportslotto_user');

        // Redirect to login page
        window.location.href = '/';

        return {
          res: 'error',
          err: 'Authentication required. Please log in.',
        };
      }

      return {
        res: 'error',
        err: `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('API GET error:', error);
    return {
      res: 'error',
      err: error instanceof Error ? error.message : 'Network error',
    };
  }
}

/**
 * Accept a ticket - Adds it to the cart
 * Sends ticket data to Django backend to save in cart
 * @param ticketData - Complete ticket data from WebSocket
 */
export async function acceptTicket(ticketData: TicketData): Promise<ApiResponse<{
  old: string;
  count: number;
  tickets: any[];
}>> {
  const url = `${API_PREFIX}game/tickets/accept/`;

  // Build FormData exactly as Django expects
  const formData = new FormData();
  formData.append('matches', ticketData.muuids.join(','));
  formData.append('type', ticketData.outcomes.join(','));
  formData.append('lines', ticketData.lines.join(','));
  formData.append('stake', ticketData.stake.toString());
  formData.append('returns', ticketData.returns.toString());
  formData.append('outcome_meta', JSON.stringify(ticketData.outcome_meta));
  formData.append('uuid', ticketData.uuid);

  console.log('📤 Posting ticket to accept endpoint:', {
    matches: ticketData.muuids.join(','),
    type: ticketData.outcomes.join(','),
    lines: ticketData.lines.join(','),
    stake: ticketData.stake,
    returns: ticketData.returns,
    uuid: ticketData.uuid,
    depth: ticketData.depth,
  });

  return apiPost(url, formData);
}

/**
 * Reject a ticket - Removes it from display and cart
 * @param uuid - The ticket UUID
 */
export async function rejectTicket(uuid: string): Promise<ApiResponse<RejectTicketResponse>> {
  const url = `${API_PREFIX}game/tickets/reject/${uuid}?ng=1`;
  const formData = new FormData();
  return apiPost<RejectTicketResponse>(url, formData);
}

/**
 * Get current cart contents
 */
export async function getCart(): Promise<ApiResponse<CartResponse>> {
  const url = `${API_PREFIX}game/tickets/cart/`;
  return apiGet<CartResponse>(url);
}

/**
 * Empty the entire cart
 */
export async function emptyCart(): Promise<ApiResponse<{ count: number }>> {
  const url = `${API_PREFIX}game/tickets/cart/empty`;
  return apiPost<{ count: number }>(url, {});
}

/**
 * Get current balance
 */
export async function getBalance(): Promise<ApiResponse<{
  balance: number;
  available: number;
  pending: number;
  bonus: number;
}>> {
  const url = `${API_PREFIX}game/get/curr_balance`;
  return apiGet(url);
}

/**
 * Submit ticket purchase (checkout)
 * @param formData - Form data with ticket UUIDs and payment options
 */
export async function submitTicketPurchase(formData: FormData): Promise<ApiResponse<{
  available: number;
  balance: number;
  pending: number;
  bonus: number;
}>> {
  const url = `${API_PREFIX}game/tickets/purchase/`; // Adjust based on your actual endpoint
  return apiPost(url, formData);
}

/**
 * Get ticket details for viewer modal
 * @param uuid - The ticket UUID
 */
export async function getTicketDetails(uuid: string): Promise<ApiResponse<any>> {
  const url = `${API_PREFIX}game/ticket/details/viewer/${uuid}`;
  return apiGet(url);
}