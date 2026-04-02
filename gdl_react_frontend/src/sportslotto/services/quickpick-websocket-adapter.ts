/**
 * Quick Picks WebSocket Adapter
 * Handles Lucky Pick / Quick Pick ticket generation
 * Tickets go directly to cart (no flip cards)
 */

import { ticketWebSocket } from '../../services/websocket-service';
import { acceptTicket } from './api';

export interface QuickPickFormData {
  stake: number;          // Wager per ticket
  count: number;          // Number of tickets to generate
  min_payout?: number;    // Minimum payout (default 20)
  events_within?: number; // Timeframe in seconds (default 129600 = 36h)
  depth?: number;         // Number of events (default 4)
  sports?: string[];      // Sport UUIDs (all 7 by default)
  ruleset?: string;       // JSON ruleset from Django
  vhost?: string;         // Virtual host UUID
  vdomain?: string;       // Virtual domain UUID
  account?: string;       // Account UUID
}

export interface QuickPickCartEntry {
  uuid: string;
  risk: number;
  returns: number;
  events: number;
  legs: any[];
}

export interface QuickPickBatchComplete {
  type: 'complete';
  ticket_count: number;
  total_risk: number;
  total_wins: number;
}

/**
 * Convert form data to Django WebSocket payload format
 * Matches the exact format from old jQuery QuickPicksForm
 */
function formToDjangoPayload(formData: QuickPickFormData) {
  const settings: Record<string, any> = {
    stake: formData.stake,
    count: formData.count,
    min_payout: formData.min_payout || 20,
    events_within: formData.events_within || 129600, // 36 hours
    depth: formData.depth || 4,
  };

  // Add sports as group_1, group_2, etc. (all 7 sports for quick picks)
  if (formData.sports && formData.sports.length > 0) {
    formData.sports.forEach((sportUuid, index) => {
      settings[`group_${index + 1}`] = sportUuid;
    });
  }

  // Add metadata
  if (formData.ruleset) settings.ruleset = formData.ruleset;
  if (formData.vhost) settings.vhost = formData.vhost;
  if (formData.vdomain) settings.vdomain = formData.vdomain;
  if (formData.account) settings.account = formData.account;

  return {
    action: 'generate',
    settings,
  };
}

/**
 * Generate quick pick tickets via WebSocket
 * Tickets are sent to cart directly (no accept/reject flow)
 * Each ticket is automatically accepted to the cart via API
 */
export function generateQuickPicks(
  formData: QuickPickFormData,
  onTicket: (entry: QuickPickCartEntry) => void,
  onComplete: (summary: QuickPickBatchComplete) => void,
  onError: (error: string) => void
): string {
  // Build Django payload
  const djangoPayload = formToDjangoPayload(formData);

  console.log('🎰 Quick Picks: Sending payload to WebSocket:', djangoPayload);

  const tickets: QuickPickCartEntry[] = [];

  // Send to Django via WebSocket
  return ticketWebSocket.sendRawQuickPickPayload(djangoPayload, async (response: any) => {
    console.log('🎰 Quick Picks: WebSocket response:', response);

    if (response.type === 'ticket') {
      // Convert to cart entry
      const entry: QuickPickCartEntry = {
        uuid: response.uuid,
        risk: response.total_stake,
        returns: response.total_returns,
        events: response.depth,
        legs: response.legs || [],
      };

      console.log('🎫 Quick Pick ticket received:', entry);

      // Quick picks are auto-accepted - add to cart via API
      // The ticket already exists in Django's database, we just need to accept it
      try {
        // Build ticket data for accept API
        // QuickPick tickets come pre-built from Django, so we use a simplified accept
        const ticketData: any = {
          uuid: response.uuid,
          muuids: response.muuids || [],
          outcomes: response.outcomes || [],
          lines: response.lines || [],
          stake: response.total_stake,
          returns: response.total_returns,
          outcome_meta: response.outcome_meta || {},
          depth: response.depth,
        };

        console.log('📤 Auto-accepting QuickPick ticket:', ticketData);

        // Accept the ticket (adds to cart)
        const result = await acceptTicket(ticketData);

        if (result.res === 'ok') {
          console.log('✅ QuickPick ticket accepted to cart:', result);
          tickets.push(entry);
          onTicket(entry);
        } else {
          console.error('❌ Failed to accept QuickPick ticket:', result.err);
          onError(result.err || 'Failed to add ticket to cart');
        }
      } catch (error) {
        console.error('❌ Error accepting QuickPick ticket:', error);
        onError(error instanceof Error ? error.message : 'Failed to add ticket to cart');
      }

    } else if (response.type === 'complete') {
      // Batch complete
      console.log('✅ QuickPick batch complete:', response);
      onComplete({
        type: 'complete',
        ticket_count: response.ticket_count,
        total_risk: response.total_risk,
        total_wins: response.total_wins,
      });

    } else if (response.type === 'error' || response.error) {
      console.error('❌ QuickPick error:', response);
      onError(response.message || response.error || 'Failed to generate quick picks');

    } else if (response.type === 'incomplete' || response.incomplete) {
      console.error('❌ Not enough events:', response);
      onError('Not enough events available for quick picks');
    }
  });
}

/**
 * Calculate possible return for quick picks (20:1 odds)
 */
export function calculateQuickPickReturn(stake: number): number {
  return stake * 20;
}
