from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional

from django.utils.timezone import now
from django.db import transaction as db_transaction

from cashier.engine import Cashier
from cashier.models import (
    EthereumWallet,
    EthereumTransaction,
    ProviderTX,
    EthereumNodeParameter
)
from cashier.providers.hotwallet.api import EthereumNodeClient
from cashier.providers.hotwallet.wallets import sweep_hot_wallet_to_house


class EthereumTransactionMonitor:
    """
    Monitors Ethereum blockchain for incoming transactions to hot wallets.
    This should be called periodically by a daemon or cron job.
    """

    def __init__(self, vhost):
        """
        Initialize the transaction monitor.

        Args:
            vhost: The virtual host object
        """
        self.vhost = vhost
        self.client = EthereumNodeClient(vhost)
        self.config = self._get_or_create_config()

    def _get_or_create_config(self) -> EthereumNodeParameter:
        """
        Get or create the Ethereum configuration for this vhost.

        Returns:
            EthereumNodeParameter object
        """
        config, created = EthereumNodeParameter.objects.get_or_create(
            vhost=self.vhost,
            defaults={
                'rpc_endpoint': 'http://localhost:8545',
                'chain_id': 1,
                'required_confirmations': 12,
                'polling_interval_seconds': 15,
                'is_active': True
            }
        )
        return config

    def check_all_wallets(self) -> Dict[str, int]:
        """
        Check all active wallets for new transactions.

        Returns:
            Dict with counts of new, confirmed, and failed transactions
        """
        if not self.config.is_active:
            print(f"Ethereum monitoring disabled for vhost {self.vhost}")
            return {"new": 0, "confirmed": 0, "failed": 0}

        # Get current block number
        try:
            current_block = self.client.eth_blockNumber()
        except Exception as e:
            print(f"Error getting current block: {e}")
            return {"new": 0, "confirmed": 0, "failed": 0, "error": str(e)}

        # Get all active wallets for this vhost
        active_wallets = EthereumWallet.objects.filter(
            vhost=self.vhost,
            is_active=True,
            deposit_received=False
        )

        stats = {
            "new": 0,
            "confirmed": 0,
            "failed": 0,
            "checked": 0
        }

        for wallet in active_wallets:
            try:
                result = self.check_wallet_transactions(wallet, current_block)
                stats["new"] += result.get("new", 0)
                stats["confirmed"] += result.get("confirmed", 0)
                stats["failed"] += result.get("failed", 0)
                stats["checked"] += 1
            except Exception as e:
                print(f"Error checking wallet {wallet.address}: {e}")

        # Update confirmations for pending transactions
        self.update_pending_transaction_confirmations(current_block)

        # Clean up expired wallets (no deposit after 1 hour)
        expired_count = self.cleanup_expired_wallets()
        stats["expired"] = expired_count

        return stats

    def check_wallet_transactions(
        self,
        wallet: EthereumWallet,
        current_block: int
    ) -> Dict[str, int]:
        """
        Check a specific wallet for new transactions.

        Args:
            wallet: EthereumWallet object to check
            current_block: Current blockchain block number

        Returns:
            Dict with counts of new, confirmed, failed transactions
        """
        stats = {"new": 0, "confirmed": 0, "failed": 0}

        try:
            # Get current balance
            balance_wei = self.client.eth_getBalance(wallet.address)

            if balance_wei > 0:
                # We detected a balance, now we need to find the transaction(s)
                # Since we don't have transaction history API in basic JSON-RPC,
                # we'll scan recent blocks for transactions to this address
                transactions = self._scan_blocks_for_address(
                    wallet.address,
                    wallet.last_checked_block + 1,
                    current_block
                )

                for tx_data in transactions:
                    # Create or update EthereumTransaction record
                    eth_tx, created = self._process_transaction(
                        tx_data,
                        wallet,
                        current_block
                    )

                    if created:
                        stats["new"] += 1

                    # Check if transaction has enough confirmations
                    if eth_tx.confirmations >= self.config.required_confirmations:
                        if eth_tx.status == 'pending':
                            self._confirm_deposit(wallet, eth_tx)
                            stats["confirmed"] += 1

            # Update last checked block
            wallet.last_checked_block = current_block
            wallet.save(update_fields=['last_checked_block', 'updated_at'])

        except Exception as e:
            print(f"Error checking wallet {wallet.address}: {e}")
            raise

        return stats

    def _scan_blocks_for_address(
        self,
        address: str,
        from_block: int,
        to_block: int
    ) -> List[Dict]:
        """
        Scan blocks for transactions to a specific address.
        Note: This is a simplified implementation. For production,
        consider using eth_getLogs with event filters or an indexer.

        Args:
            address: Ethereum address to search for
            from_block: Starting block number
            to_block: Ending block number

        Returns:
            List of transaction dictionaries
        """
        transactions = []
        address = address.lower()

        # Limit scan to prevent timeouts
        max_blocks_to_scan = 1000
        scan_from = max(from_block, to_block - max_blocks_to_scan)

        for block_num in range(scan_from, to_block + 1):
            try:
                block = self.client.eth_getBlockByNumber(block_num, True)

                if block and 'transactions' in block:
                    for tx in block['transactions']:
                        if tx.get('to', '').lower() == address:
                            transactions.append(tx)

            except Exception as e:
                print(f"Error scanning block {block_num}: {e}")
                continue

        return transactions

    def _process_transaction(
        self,
        tx_data: Dict,
        wallet: EthereumWallet,
        current_block: int
    ) -> tuple:
        """
        Process a transaction and create/update EthereumTransaction record.

        Args:
            tx_data: Transaction data from blockchain
            wallet: Associated EthereumWallet
            current_block: Current block number

        Returns:
            Tuple of (EthereumTransaction, created)
        """
        tx_hash = tx_data['hash']

        # Get transaction receipt for status
        receipt = self.client.eth_getTransactionReceipt(tx_hash)

        if not receipt:
            # Transaction not mined yet
            return None, False

        # Calculate amounts
        amount_wei = Decimal(int(tx_data['value'], 16))
        amount_eth = self.client.wei_to_eth(amount_wei)

        # Calculate confirmations
        block_number = int(receipt['blockNumber'], 16)
        confirmations = current_block - block_number + 1

        # Determine status
        tx_status = 'pending'
        if int(receipt.get('status', '0x0'), 16) == 0:
            tx_status = 'failed'
        elif confirmations >= self.config.required_confirmations:
            tx_status = 'confirmed'

        # Calculate transaction fee
        gas_used = int(receipt.get('gasUsed', '0x0'), 16)
        gas_price = int(tx_data.get('gasPrice', '0x0'), 16)
        tx_fee = gas_used * gas_price

        # Create or update transaction record
        eth_tx, created = EthereumTransaction.objects.update_or_create(
            tx_hash=tx_hash,
            defaults={
                'vhost': wallet.vhost,
                'from_address': tx_data['from'],
                'to_address': tx_data['to'],
                'wallet': wallet,
                'amount_wei': amount_wei,
                'amount_eth': amount_eth,
                'gas_used': gas_used,
                'gas_price': gas_price,
                'transaction_fee_wei': tx_fee,
                'block_number': block_number,
                'block_hash': receipt.get('blockHash'),
                'confirmations': confirmations,
                'status': tx_status,
                'provider_tx': wallet.provider_tx,
                'nonce': int(tx_data.get('nonce', '0x0'), 16),
                'transaction_index': int(receipt.get('transactionIndex', '0x0'), 16),
                'input_data': tx_data.get('input', '0x')
            }
        )

        if tx_status == 'confirmed' and not eth_tx.confirmed_at:
            eth_tx.confirmed_at = now()
            eth_tx.save(update_fields=['confirmed_at'])

        return eth_tx, created

    def _confirm_deposit(self, wallet: EthereumWallet, eth_tx: EthereumTransaction):
        """
        Confirm a deposit and credit the account.

        Args:
            wallet: EthereumWallet that received the deposit
            eth_tx: EthereumTransaction that was confirmed
        """
        with db_transaction.atomic():
            # Get the ProviderTX
            provider_tx = wallet.provider_tx

            # Check if already processed
            if provider_tx.completed:
                print(f"Deposit already completed for wallet {wallet.address}")
                return

            # Update ProviderTX status
            provider_tx.status = '4'  # Payment Received
            provider_tx.confirmed_at = now()
            provider_tx.save()

            # Update wallet
            wallet.deposit_received = True
            wallet.is_active = False
            wallet.first_deposit_at = now()
            wallet.save()

            # Credit the account using Cashier
            cashier = Cashier(account=provider_tx.account,vhost=provider_tx.account.vhost)
            final_amount = eth_tx.amount_eth

            print(f"Confirming deposit: {final_amount} ETH to account {provider_tx.account}")
            cashier.confirm_pending_deposit(provider_tx, final_amount)

            # Update ProviderTX to completed
            provider_tx.status = '5'  # Invoice Complete
            provider_tx.completed = True
            provider_tx.completed_at = now()
            provider_tx.save()

            print(f"Deposit confirmed: {final_amount} ETH for wallet {wallet.address}")

        # After user is credited, sweep funds to house wallet (outside atomic transaction)
        try:
            self._sweep_to_house_wallet(wallet)
        except Exception as e:
            print(f"⚠️  Error sweeping funds from {wallet.address}: {e}")
            # User already credited, log error for manual intervention
            # Don't raise - we'll retry on next monitoring cycle

    def _sweep_to_house_wallet(self, wallet: EthereumWallet):
        """
        Sweep all funds from hot wallet to house wallet.

        Args:
            wallet: EthereumWallet to sweep funds from
        """
        # Check if already swept
        if not wallet.encrypted_private_key:
            print(f"Wallet {wallet.address} already swept (no private key)")
            return

        print(f"🔄 Initiating sweep from {wallet.address} to house wallet...")

        # Execute sweep
        sweep_result = sweep_hot_wallet_to_house(
            vhost=wallet.vhost,
            encrypted_private_key=wallet.encrypted_private_key,
            hot_wallet_address=wallet.address,
            rpc_client=self.client
        )

        print(
            f"✅ Sweep transaction sent: {sweep_result['tx_hash']}\n"
            f"   Amount: {sweep_result['amount_eth']} ETH\n"
            f"   Gas cost: {sweep_result['gas_cost_eth']} ETH\n"
            f"   House wallet: {sweep_result['house_wallet']}"
        )

        # Create EthereumTransaction record for the sweep
        current_block = self.client.eth_blockNumber()

        sweep_tx = EthereumTransaction.objects.create(
            vhost=wallet.vhost,
            tx_hash=sweep_result['tx_hash'],
            from_address=wallet.address,
            to_address=sweep_result['house_wallet'],
            wallet=wallet,
            amount_wei=int(Decimal(sweep_result['amount_eth']) * Decimal(10 ** 18)),
            amount_eth=Decimal(str(sweep_result['amount_eth'])),
            status='pending',
            confirmations=0,
            provider_tx=wallet.provider_tx
        )

        print(f"📝 Sweep transaction recorded: {sweep_tx.tx_hash}")

    def _cleanup_wallet_after_sweep(self, wallet: EthereumWallet, sweep_tx: EthereumTransaction):
        """
        Clean up wallet after successful sweep to house wallet.
        Deletes private key and marks wallet as fully processed.

        Args:
            wallet: EthereumWallet to clean up
            sweep_tx: The confirmed sweep transaction
        """
        print(f"🧹 Cleaning up wallet {wallet.address}...")

        with db_transaction.atomic():
            # Delete encrypted private key (can't spend from this wallet anymore)
            wallet.encrypted_private_key = None
            wallet.is_active = False
            wallet.save()

            print(f"✅ Wallet {wallet.address} cleaned up successfully")

    def cleanup_expired_wallets(self) -> int:
        """
        Clean up wallets that have been active for over 1 hour without receiving a deposit.
        These are abandoned deposits where the user never completed the 3rd party flow.

        Returns:
            Number of wallets cleaned up
        """
        from datetime import timedelta

        # Find wallets that are:
        # 1. Still active
        # 2. Haven't received a deposit
        # 3. Created more than 1 hour ago
        expiration_time = now() - timedelta(hours=1)

        expired_wallets = EthereumWallet.objects.filter(
            vhost=self.vhost,
            is_active=True,
            deposit_received=False,
            created_at__lt=expiration_time
        )

        count = 0
        for wallet in expired_wallets:
            try:
                print(f"⏰ Expiring wallet {wallet.address} (created {wallet.created_at})")

                with db_transaction.atomic():
                    # Update ProviderTX to expired status
                    provider_tx = wallet.provider_tx
                    provider_tx.status = '103'  # Expired w/o payment
                    provider_tx.cancelled_at = now()
                    provider_tx.active = False
                    provider_tx.save()

                    # Delete private key and deactivate wallet
                    wallet.encrypted_private_key = None
                    wallet.is_active = False
                    wallet.save()

                print(f"✅ Wallet {wallet.address} expired and cleaned up")
                count += 1

            except Exception as e:
                print(f"⚠️  Error expiring wallet {wallet.address}: {e}")

        if count > 0:
            print(f"🧹 Cleaned up {count} expired wallet(s)")

        return count

    def update_pending_transaction_confirmations(self, current_block: int):
        """
        Update confirmation counts for all pending transactions.

        Args:
            current_block: Current block number
        """
        pending_txs = EthereumTransaction.objects.filter(
            vhost=self.vhost,
            status='pending'
        ).exclude(block_number__isnull=True)

        for eth_tx in pending_txs:
            try:
                eth_tx.update_confirmations(current_block)

                # Check if now has enough confirmations
                if eth_tx.confirmations >= self.config.required_confirmations:
                    # Mark as confirmed
                    eth_tx.status = 'confirmed'
                    eth_tx.confirmed_at = now()
                    eth_tx.save()

                    # Check if this is an incoming deposit (to hot wallet)
                    if eth_tx.wallet and not eth_tx.wallet.deposit_received:
                        self._confirm_deposit(eth_tx.wallet, eth_tx)

                    # Check if this is an outgoing sweep (from hot wallet to house)
                    elif eth_tx.wallet and eth_tx.from_address.lower() == eth_tx.wallet.address.lower():
                        # This is a sweep transaction - clean up the wallet
                        if eth_tx.wallet.encrypted_private_key:  # Only if not already cleaned
                            self._cleanup_wallet_after_sweep(eth_tx.wallet, eth_tx)

            except Exception as e:
                print(f"Error updating confirmations for {eth_tx.tx_hash}: {e}")


def monitor_all_vhosts():
    """
    Monitor all vhosts for Ethereum transactions.
    This function should be called by a daemon or cron job.

    Returns:
        Dict with overall statistics
    """
    from parameters.models import VHost

    overall_stats = {
        "vhosts_checked": 0,
        "total_new": 0,
        "total_confirmed": 0,
        "total_failed": 0,
        "errors": []
    }

    # Get all vhosts with active Ethereum configs
    vhosts = VHost.objects.filter(
        ethereum_config__is_active=True
    ).distinct()

    for vhost in vhosts:
        try:
            monitor = EthereumTransactionMonitor(vhost)
            stats = monitor.check_all_wallets()

            overall_stats["vhosts_checked"] += 1
            overall_stats["total_new"] += stats.get("new", 0)
            overall_stats["total_confirmed"] += stats.get("confirmed", 0)
            overall_stats["total_failed"] += stats.get("failed", 0)

            print(f"Checked vhost {vhost}: {stats}")

        except Exception as e:
            error_msg = f"Error monitoring vhost {vhost}: {e}"
            print(error_msg)
            overall_stats["errors"].append(error_msg)

    return overall_stats


def check_single_wallet(wallet_address: str) -> Optional[Dict]:
    """
    Check a single wallet by address.
    Useful for manual checking or debugging.

    Args:
        wallet_address: Ethereum address to check

    Returns:
        Dict with wallet status and transactions, or None if not found
    """
    try:
        wallet = EthereumWallet.objects.get(address=wallet_address)
        monitor = EthereumTransactionMonitor(wallet.vhost)
        current_block = monitor.client.eth_blockNumber()

        stats = monitor.check_wallet_transactions(wallet, current_block)

        return {
            "wallet": wallet_address,
            "status": "active" if wallet.is_active else "inactive",
            "deposit_received": wallet.deposit_received,
            "last_checked_block": wallet.last_checked_block,
            "current_block": current_block,
            "stats": stats
        }

    except EthereumWallet.DoesNotExist:
        return None
