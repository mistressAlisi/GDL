/**
 * Ticket WebSocket Adapter
 * Bridges React components to Django WebSocket format
 */

import { ticketWebSocket } from '../../services/websocket-service';

/**
 * Django ticket response format (from backend)
 */
export interface DjangoTicketResponse {
  type: 'ticket' | 'complete' | 'error' | 'incomplete';
  uuid?: string;
  request_id?: string;
  depth: number;
  total_stake: number;
  total_returns: number;
  total_odds?: number;
  legs?: any[];
  muuids?: string[];
  outcomes?: string[];
  lines?: string[];
  outcome_meta?: any;
  status: string; // 'C' = created, 'P' = pending, 'W' = won, 'L' = lost
  old_uuid?: string;
  message?: string;
  error?: string;
  incomplete?: boolean;
}

/**
 * Custom ticket form data (from React form)
 */
export interface CustomTicketFormData {
  stake: number;
  depth: number;
  min_payout: number; // Minimum payout multiplier
  sports: string[];
  events_within: number; // seconds
  count?: number;
  vhost: string;
  vdomain: string;
  account: string;
}

/**
 * Quick Pick form data
 */
export interface QuickPickFormData {
  stake: number;
  count?: number;
  vhost: string;
  vdomain: string;
  account: string;
}

/**
 * Convert form data to Django WebSocket payload format
 */
function formToDjangoPayload(formData: CustomTicketFormData, oldUuid?: string): any {
  console.log('🔧 formToDjangoPayload called with:', formData);

  const payload = {
    action: 'generate',
    settings: {
      stake: formData.stake,
      depth: formData.depth,
      min_payout: formData.min_payout,
      sports: formData.sports.join(','),
      events_within: formData.events_within,
      count: formData.count || 1,
      // Required UUIDs for Django backend
      vhost: formData.vhost,
      vdomain: formData.vdomain,
      account: formData.account,
    }
  };

  // Add old_uuid for ticket replacement
  if (oldUuid) {
    payload.old_uuid = oldUuid;
  }

  console.log('🔍 Final payload:', payload);

  return payload;
}

/**
 * Convert seconds to hours string format for WebSocket
 */
function secondsToHoursString(seconds: number): string {
  const hours = Math.round(seconds / 3600);
  return `${hours}h`;
}

/**
 * Generate custom tickets via WebSocket
 * Sends Django-formatted payload directly to /stream_tickets consumer
 */
export function generateCustomTickets(
  formData: CustomTicketFormData,
  onTicket: (ticket: DjangoTicketResponse) => void,
  onError: (error: string) => void
): string {
  const count = formData.count || 1;

  console.log('🎫 generateCustomTickets called with:', {
    count,
    stake: formData.stake,
    depth: formData.depth,
    sports: formData.sports,
    events_within: formData.events_within,
  });

  // Build Django payload
  const djangoPayload = formToDjangoPayload(formData);

  console.log('📦 Django payload:', JSON.stringify(djangoPayload, null, 2));

  // Send directly via WebSocket service
  // The service will handle the response
  return sendDjangoPayload(djangoPayload, onTicket, onError);
}

/**
 * Replace a ticket (reject and get new one)
 */
export function replaceTicket(
  formData: CustomTicketFormData,
  oldUuid: string,
  onTicket: (ticket: DjangoTicketResponse, oldUuid: string) => void,
  onError: (error: string) => void
): string {
  // CRITICAL: Override count to 1 for replacements (ignore original formData.count)
  const replacementFormData = {
    ...formData,
    count: 1, // ALWAYS 1 for replacements
  };

  // Build Django payload with old_uuid
  const djangoPayload = formToDjangoPayload(replacementFormData, oldUuid);

  // Send directly via WebSocket service
  return sendDjangoPayload(djangoPayload, (ticket) => {
    onTicket(ticket, oldUuid);
  }, onError);
}

/**
 * Send Django-formatted payload to WebSocket
 * This bypasses the internal format conversion and sends directly to Django
 */
function sendDjangoPayload(
  payload: any,
  onTicket: (ticket: DjangoTicketResponse) => void,
  onError: (error: string) => void
): string {
  const requestId = `ticket_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  console.log('📨 sendDjangoPayload called!');
  console.log('   payload BEFORE adding requestId:', JSON.stringify(payload, null, 2));

  // Add requestId to payload for tracking
  const payloadWithId = {
    ...payload,
    requestId,
  };

  console.log('   payload AFTER adding requestId:', JSON.stringify(payloadWithId, null, 2));
  console.log('   calling ticketWebSocket.sendRawTicketPayload()...');

  // Track received tickets count
  let ticketsReceived = 0;
  const expectedCount = payload.settings?.count || 1;

  // Use the low-level WebSocket send
  // Register handler that will be called for ALL messages with this requestId
  ticketWebSocket.sendRawTicketPayload(payloadWithId, (response: any) => {
    console.log('🎯 sendDjangoPayload handler called with response:', response);

    if (response.type === 'ticket') {
      ticketsReceived++;
      console.log(`🎫 Ticket ${ticketsReceived}/${expectedCount} received`);
      onTicket(response as DjangoTicketResponse);
    } else if (response.type === 'complete') {
      console.log('✅ Ticket generation complete:', response);
      // Don't need to do anything here, tickets have already been processed
    } else if (response.type === 'error' || response.error) {
      console.error('❌ Error response:', response);
      onError(response.message || response.error || 'Failed to generate ticket');
    } else if (response.type === 'incomplete') {
      console.warn('⚠️ Incomplete response:', response);
      onError('Not enough events available for the selected criteria');
    } else {
      console.warn('⚠️ Unknown response type:', response.type);
    }
  });

  return requestId;
}

/**
 * Generate quick pick tickets via WebSocket
 * Sends Django-formatted payload directly to /stream_quickpicks consumer
 */
export function generateQuickPicks(
  formData: QuickPickFormData,
  onTicket: (ticket: DjangoTicketResponse) => void,
  onError: (error: string) => void
): string {
  const payload = {
    action: 'generate',
    settings: {
      stake: formData.stake,
      count: formData.count || 1,
      // Required UUIDs for Django backend
      vhost: formData.vhost,
      vdomain: formData.vdomain,
      account: formData.account,
    }
  };

  console.log('🎲 generateQuickPicks called with payload:', payload);

  return sendDjangoPayload(payload, onTicket, onError);
}