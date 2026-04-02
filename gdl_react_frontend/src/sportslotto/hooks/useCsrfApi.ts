/**
 * React Hook for CSRF-protected API calls
 * Provides loading states, error handling, and automatic CSRF token management
 */

import { useState, useCallback } from 'react';
import { csrfPost, csrfPut, csrfPatch, csrfDelete, csrfGet } from '../utils/csrf';

interface UseApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

/**
 * Hook for making API calls with automatic CSRF token handling
 *
 * @example
 * const { data, loading, error, execute } = useCsrfApi(
 *   (username, password) => csrfPost('/api/v1/account/login/', { username, password }),
 *   {
 *     onSuccess: (data) => console.log('Login successful', data),
 *     onError: (error) => toast.error(error.message),
 *   }
 * );
 *
 * // Later in your component:
 * await execute('john', 'password123');
 */
export function useCsrfApi<T = any>(
  apiCall: (...args: any[]) => Promise<T>,
  options?: UseApiOptions
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setState({ data: null, loading: true, error: null });

      try {
        const result = await apiCall(...args);
        setState({ data: result, loading: false, error: null });
        options?.onSuccess?.(result);
        return result;
      } catch (error) {
        const err = error instanceof Error ? error : new Error('Unknown error occurred');
        setState({ data: null, loading: false, error: err });
        options?.onError?.(err);
        return null;
      }
    },
    [apiCall, options]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

/**
 * Convenience hooks for common HTTP methods
 */

export function useCsrfPost<T = any>(url: string, options?: UseApiOptions) {
  return useCsrfApi<T>((data) => csrfPost<T>(url, data), options);
}

export function useCsrfPut<T = any>(url: string, options?: UseApiOptions) {
  return useCsrfApi<T>((data) => csrfPut<T>(url, data), options);
}

export function useCsrfPatch<T = any>(url: string, options?: UseApiOptions) {
  return useCsrfApi<T>((data) => csrfPatch<T>(url, data), options);
}

export function useCsrfDelete<T = any>(url: string, options?: UseApiOptions) {
  return useCsrfApi<T>(() => csrfDelete<T>(url), options);
}

export function useCsrfGet<T = any>(url: string, options?: UseApiOptions) {
  return useCsrfApi<T>(() => csrfGet<T>(url), options);
}
