import React, { useState, useEffect, useCallback } from 'react';

// API Response Types
export interface TableColumn {
  key: string;
  name: string;
  sortable?: boolean;
  searchable?: boolean;
}

export interface TablePaginator {
  current_page: number;
  total_pages: number;
  total_records: number;
  page_size: number;
}

export interface TableResponse {
  res: 'ok' | 'error';
  data?: {
    rows: any[];
    columns: string[];
    column_names: Record<string, string>;
    paginator: TablePaginator;
    additional_cols?: Record<string, any>;
    totals?: Record<string, { name: string; value: string | number }>;
    empty?: boolean;
  };
  err?: string;
}

export interface DataTableProps {
  endpoint: string;  // e.g., "tickets/previous/table/"
  pageSize?: number;
  className?: string;
  onRowClick?: (row: any) => void;
  additionalColumns?: {
    key: string;
    name: string;
    render: (row: any) => React.ReactNode;
  }[];
  displayColumns?: string[];  // Optional: filter which columns to show
  enableSearch?: boolean;
  enableSort?: boolean;
  enablePagination?: boolean;
  customRowClass?: (row: any) => string;
  emptyMessage?: string;
  filterString?: string;  // Custom filter string
  customColumnRender?: (value: any, columnKey: string, row: any) => React.ReactNode;  // Custom column rendering
}

interface SortState {
  column: string;
  mode: 'none' | 'ASC' | 'DESC';
}

interface SearchState {
  [key: string]: string;
}

// Get CSRF token
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

// Get API prefix from URL path
function getApiPrefix(): string {
  const pathParts = window.location.pathname.split('/').filter(p => p);
  if (pathParts.length > 0) {
    return `/api/v1/${pathParts[0]}/`;
  }
  return '/api/v1/';
}

export function DataTable({
  endpoint,
  pageSize = 15,
  className = '',
  onRowClick,
  additionalColumns = [],
  displayColumns = [],
  enableSearch = true,
  enableSort = true,
  enablePagination = true,
  customRowClass,
  emptyMessage = 'No records found',
  filterString = '',
  customColumnRender,
}: DataTableProps) {
  const [data, setData] = useState<any[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [columnNames, setColumnNames] = useState<Record<string, string>>({});
  const [paginator, setPaginator] = useState<TablePaginator>({
    current_page: 1,
    total_pages: 0,
    total_records: 0,
    page_size: pageSize,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortState, setSortState] = useState<Record<string, SortState>>({});
  const [searchState, setSearchState] = useState<SearchState>({});
  const [totals, setTotals] = useState<Record<string, { name: string; value: string | number }>>({});

  const API_PREFIX = getApiPrefix();

  // Build sort query string
  const buildSortQueryString = useCallback(() => {
    const sortParts: string[] = [];
    Object.entries(sortState).forEach(([key, state]) => {
      if (state.mode === 'ASC') {
        sortParts.push(state.column);
      } else if (state.mode === 'DESC') {
        sortParts.push(`-${state.column}`);
      }
    });
    return sortParts.length > 0 ? `&srt=${sortParts.join(';')}` : '';
  }, [sortState]);

  // Fetch table data
  const fetchData = useCallback(async (page: number = 1) => {
    setLoading(true);
    setError(null);

    try {
      const cols = displayColumns.length > 0 ? displayColumns.join(',') : columns.join(',');
      const sortQuery = buildSortQueryString();
      const url = `${API_PREFIX}${endpoint}${pageSize}/${page}?cols=${cols}${sortQuery}&filter=${filterString}`;

      console.log('📊 Fetching table data:', url);

      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
      });

      console.log('📥 Table response status:', response.status);

      if (!response.ok) {
        if (response.status === 401) {
          alert('Session Expired\n\nYour session has expired. Please log in again.');
          localStorage.removeItem('sportslotto_user');
          window.location.href = '/';
          throw new Error('Session expired');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result: TableResponse = await response.json();
      console.log('✅ Table data:', result);

      if (result.res === 'error') {
        throw new Error(result.err || 'Failed to load table data');
      }

      if (result.data) {
        if (result.data.empty) {
          // Empty table
          setData([]);
          setColumns([]);
          setColumnNames({});
          setPaginator({
            current_page: 0,
            total_pages: 0,
            total_records: 0,
            page_size: pageSize,
          });
        } else {
          setData(result.data.rows || []);
          setColumns(result.data.columns || []);
          setColumnNames(result.data.column_names || {});
          setPaginator(result.data.paginator);
          if (result.data.totals) {
            setTotals(result.data.totals);
          }
        }
      }
    } catch (err) {
      console.error('❌ Table fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [endpoint, pageSize, columns, displayColumns, buildSortQueryString, filterString, API_PREFIX]);

  // Initialize table
  const initializeTable = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const url = `${API_PREFIX}${endpoint}${pageSize}?filter=${filterString}`;
      console.log('📊 Initializing table:', url);

      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) {
        if (response.status === 401) {
          alert('Session Expired\n\nYour session has expired. Please log in again.');
          localStorage.removeItem('sportslotto_user');
          window.location.href = '/';
          throw new Error('Session expired');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result: TableResponse = await response.json();
      console.log('✅ Table initialized:', result);

      if (result.res === 'error') {
        throw new Error(result.err || 'Failed to initialize table');
      }

      if (result.data) {
        if (result.data.empty) {
          // Empty table
          setData([]);
          setColumns([]);
          setColumnNames({});
          setPaginator({
            current_page: 0,
            total_pages: 0,
            total_records: 0,
            page_size: pageSize,
          });
          setLoading(false);
        } else {
          // Set columns based on column_names (only displayed columns)
          const displayedColumns = Object.keys(result.data.column_names || {});
          setColumns(displayedColumns);
          setColumnNames(result.data.column_names || {});
          setPaginator(result.data.paginator);
          // Load first page
          fetchData(1);
        }
      }
    } catch (err) {
      console.error('❌ Table init error:', err);
      setError(err instanceof Error ? err.message : 'Failed to initialize table');
      setLoading(false);
    }
  }, [endpoint, pageSize, filterString, API_PREFIX, fetchData]);

  // Initialize on mount
  useEffect(() => {
    initializeTable();
  }, [initializeTable]);

  // Handle page navigation
  const handlePageChange = (page: number) => {
    if (page < 1 || page > paginator.total_pages) return;
    fetchData(page);
  };

  // Handle sort
  const handleSort = (columnKey: string) => {
    if (!enableSort) return;

    setSortState((prev) => {
      const currentState = prev[columnKey] || { column: columnKey, mode: 'none' };
      let newMode: 'none' | 'ASC' | 'DESC' = 'none';

      if (currentState.mode === 'none') {
        newMode = 'ASC';
      } else if (currentState.mode === 'ASC') {
        newMode = 'DESC';
      } else {
        newMode = 'none';
      }

      return {
        ...prev,
        [columnKey]: { column: columnKey, mode: newMode },
      };
    });
  };

  // Re-fetch when sort changes
  useEffect(() => {
    if (columns.length > 0) {
      fetchData(paginator.current_page);
    }
  }, [sortState]);

  // Render sort icon
  const renderSortIcon = (columnKey: string) => {
    const state = sortState[columnKey];
    if (!state || state.mode === 'none') {
      return <i className="fas fa-sort ms-2 opacity-50"></i>;
    }
    if (state.mode === 'ASC') {
      return <i className="fas fa-sort-up ms-2 text-primary"></i>;
    }
    return <i className="fas fa-sort-down ms-2 text-primary"></i>;
  };

  // Render pagination buttons
  const renderPagination = () => {
    if (!enablePagination || paginator.total_pages <= 1) return null;

    const pages: (number | string)[] = [];
    const maxButtons = 10;

    if (paginator.total_pages <= maxButtons) {
      // Show all pages
      for (let i = 1; i <= paginator.total_pages; i++) {
        pages.push(i);
      }
    } else {
      // Show interactive navigation
      const current = paginator.current_page;
      const total = paginator.total_pages;

      // Always show first page
      pages.push(1);

      // Show pages around current
      for (let i = Math.max(2, current - 2); i <= Math.min(total - 1, current + 2); i++) {
        if (pages[pages.length - 1] !== i - 1 && i > 2) {
          pages.push('...');
        }
        pages.push(i);
      }

      // Always show last page
      if (pages[pages.length - 1] !== total - 1 && total > 1) {
        pages.push('...');
      }
      if (total > 1) pages.push(total);
    }

    return (
      <nav aria-label="Table Navigation">
        <ul className="pagination mb-0">
          {/* Previous Button */}
          <button
            className="btn btn-primary me-2"
            onClick={() => handlePageChange(paginator.current_page - 1)}
            disabled={paginator.current_page === 1 || loading}
          >
            Previous
          </button>

          {/* Page Buttons */}
          {pages.map((page, idx) => {
            if (page === '...') {
              return (
                <li key={`ellipsis-${idx}`} className="page-item disabled">
                  <span className="page-link bg-transparent border-0 text-white">...</span>
                </li>
              );
            }

            const pageNum = page as number;
            const isActive = pageNum === paginator.current_page;

            return (
              <button
                key={pageNum}
                className={`btn ${isActive ? 'btn-secondary' : pageNum % 2 === 0 ? 'btn-success' : 'btn-primary'} mx-1`}
                onClick={() => handlePageChange(pageNum)}
                disabled={isActive || loading}
                style={{ minWidth: '45px' }}
              >
                {pageNum}
              </button>
            );
          })}

          {/* Next Button */}
          <button
            className="btn btn-primary ms-2"
            onClick={() => handlePageChange(paginator.current_page + 1)}
            disabled={paginator.current_page === paginator.total_pages || loading}
          >
            Next
          </button>
        </ul>
      </nav>
    );
  };

  // Calculate progress percentage
  const progressPercentage = paginator.total_records > 0
    ? Math.min(100, ((paginator.current_page * paginator.page_size) / paginator.total_records) * 100)
    : 0;

  return (
    <div className={`data-table-container ${className}`}>
      {/* Table */}
      <div className="table-responsive" style={{
        background: 'linear-gradient(135deg, rgba(30, 20, 50, 0.95) 0%, rgba(15, 10, 30, 0.95) 100%)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        border: '1px solid rgba(168, 85, 247, 0.3)',
        borderRadius: '16px',
        padding: '1rem',
        boxShadow: '0 8px 32px rgba(168, 85, 247, 0.2)',
      }}>
        <table className="table table-hover table-dark mb-0">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  style={{
                    cursor: enableSort ? 'pointer' : 'default',
                    borderBottom: '2px solid rgba(168, 85, 247, 0.5)',
                    color: '#fff',
                    fontWeight: '600',
                    padding: '1rem',
                  }}
                  onClick={() => handleSort(col)}
                >
                  {columnNames[col] || col}
                  {enableSort && renderSortIcon(col)}
                </th>
              ))}
              {additionalColumns.map((col) => (
                <th
                  key={col.key}
                  style={{
                    borderBottom: '2px solid rgba(168, 85, 247, 0.5)',
                    color: '#fff',
                    fontWeight: '600',
                    padding: '1rem',
                  }}
                >
                  {col.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={columns.length + additionalColumns.length} className="text-center py-5">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <p className="text-white mt-3 mb-0">Loading...</p>
                </td>
              </tr>
            )}

            {error && (
              <tr>
                <td colSpan={columns.length + additionalColumns.length} className="text-center py-5">
                  <i className="fas fa-exclamation-circle text-danger fa-3x mb-3"></i>
                  <p className="text-danger mb-0">{error}</p>
                </td>
              </tr>
            )}

            {!loading && !error && data.length === 0 && (
              <tr>
                <td colSpan={columns.length + additionalColumns.length} className="text-center py-5">
                  <p className="text-white-50 mb-0">{emptyMessage}</p>
                </td>
              </tr>
            )}

            {!loading && !error && data.map((row, idx) => (
              <tr
                key={row.__pk || idx}
                className={customRowClass ? customRowClass(row) : ''}
                onClick={() => onRowClick && onRowClick(row)}
                style={{
                  cursor: onRowClick ? 'pointer' : 'default',
                  transition: 'all 0.2s ease',
                }}
              >
                {columns.map((col) => (
                  <td
                    key={col}
                    style={{
                      borderBottom: '1px solid rgba(168, 85, 247, 0.2)',
                      color: 'rgba(255, 255, 255, 0.9)',
                      padding: '0.75rem 1rem',
                    }}
                  >
                    {customColumnRender
                      ? customColumnRender(row[col], col, row)
                      : (typeof row[col] === 'object' && row[col] !== null
                        ? row[col].name || row[col].id || ''
                        : row[col] || '')}
                  </td>
                ))}
                {additionalColumns.map((col) => (
                  <td
                    key={col.key}
                    style={{
                      borderBottom: '1px solid rgba(168, 85, 247, 0.2)',
                      color: 'rgba(255, 255, 255, 0.9)',
                      padding: '0.75rem 1rem',
                    }}
                  >
                    {col.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>

          {/* Totals Footer */}
          {Object.keys(totals).length > 0 && (
            <tfoot>
              <tr style={{ borderTop: '2px solid rgba(168, 85, 247, 0.5)' }}>
                {Object.values(totals).map((total, idx) => (
                  <td
                    key={idx}
                    className="text-white fw-bold"
                    style={{ padding: '1rem' }}
                  >
                    {total.name}: {total.value}
                  </td>
                ))}
              </tr>
            </tfoot>
          )}
        </table>
      </div>

      {/* Footer Navigation */}
      <div
        className="d-flex justify-content-between align-items-center mt-3 flex-wrap gap-3"
        style={{
          background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%)',
          borderRadius: '12px',
          padding: '1rem',
        }}
      >
        {/* Pagination Controls */}
        <div>{renderPagination()}</div>

        {/* Record Count */}
        <div className="text-white">
          {paginator.total_records > 0 ? (
            <>
              Viewing {Math.min(paginator.current_page * paginator.page_size, paginator.total_records)}/
              {paginator.total_records} records
            </>
          ) : (
            'No records'
          )}
        </div>

        {/* Progress Bar */}
        {paginator.total_pages > 1 && (
          <div
            className="progress"
            style={{
              width: '150px',
              height: '8px',
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '4px',
            }}
          >
            <div
              className="progress-bar progress-bar-striped bg-success"
              role="progressbar"
              style={{ width: `${progressPercentage}%` }}
              aria-valuenow={progressPercentage}
              aria-valuemin={0}
              aria-valuemax={100}
            ></div>
          </div>
        )}

        {/* Status Indicator */}
        <div className="text-white">
          {loading ? (
            <span>
              <i className="fas fa-spinner fa-spin text-primary me-2"></i>
              Loading...
            </span>
          ) : error ? (
            <span>
              <i className="fas fa-exclamation-circle text-danger me-2"></i>
              Error!
            </span>
          ) : (
            <span>
              <i className="fas fa-check-circle text-success me-2"></i>
              Ready!
            </span>
          )}
        </div>
      </div>
    </div>
  );
}