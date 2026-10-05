<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Search, RefreshCw, Receipt } from 'lucide-svelte';

  let transactions = $state<any[]>([]);
  let isLoading = $state(true);
  let search = $state('');
  let typeFilter = $state('');

  const txTypes = [
    'CASHBACK',
    'REFERRAL_BONUS',
    'PROMOTIONAL_BONUS',
    'MANUAL_CREDIT',
    'MANUAL_DEBIT',
    'REDEMPTION',
    'REVERSAL',
    'REFUND',
    'ADMIN_ADJUSTMENT'
  ];

  async function loadTransactions() {
    isLoading = true;
    try {
      const res = await api.get('/admin/transactions/', {
        search,
        type: typeFilter,
      });
      transactions = res.results || res;
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadTransactions();
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">Immutable Coin Ledger</h1>
      <p class="text-xs text-slate-400 mt-1">Complete auditable record of all CBK coin credits, debits, reversals, and payouts</p>
    </div>
    <button
      onclick={loadTransactions}
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors"
    >
      <RefreshCw size={14} class={isLoading ? 'animate-spin' : ''} />
      <span>Refresh Ledger</span>
    </button>
  </div>

  <!-- Filters -->
  <div class="cbk-card p-4 flex flex-wrap gap-4 items-center justify-between">
    <div class="relative flex-1 max-w-md">
      <Search size={15} class="absolute left-3 top-2.5 text-slate-500" />
      <input
        type="text"
        bind:value={search}
        oninput={loadTransactions}
        placeholder="Search by Tx ID, user email, reference ID, or description..."
        class="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
      />
    </div>

    <select
      bind:value={typeFilter}
      onchange={loadTransactions}
      class="bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 px-3 py-1.5 focus:outline-none"
    >
      <option value="">All Transaction Types</option>
      {#each txTypes as t}
        <option value={t}>{t.replace('_', ' ')}</option>
      {/each}
    </select>
  </div>

  <!-- Transactions Table -->
  <div class="cbk-card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="cbk-table">
        <thead>
          <tr>
            <th>Tx ID / Date</th>
            <th>Account</th>
            <th>Type</th>
            <th>Coins Delta</th>
            <th>INR Value</th>
            <th>Balance Delta</th>
            <th>Reference</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/80">
          {#if isLoading}
            <tr><td colspan="8" class="text-center py-8 text-xs text-slate-500">Loading ledger records...</td></tr>
          {:else if transactions.length === 0}
            <tr><td colspan="8" class="text-center py-8 text-xs text-slate-500">No ledger transactions found.</td></tr>
          {:else}
            {#each transactions as tx}
              {@const isDebit = tx.transaction_type.includes('DEBIT') || tx.transaction_type === 'REDEMPTION' || tx.transaction_type === 'REVERSAL'}
              <tr>
                <td>
                  <span class="font-mono text-[11px] text-indigo-400 font-semibold">{tx.tx_id.substring(0, 8)}...</span>
                  <span class="block text-[10px] text-slate-400 font-mono">{new Date(tx.created_at).toLocaleString()}</span>
                </td>
                <td>
                  <span class="text-xs font-mono text-slate-300">{tx.user_email}</span>
                </td>
                <td>
                  <StatusBadge status={tx.transaction_type} size="sm" />
                </td>
                <td>
                  <span class="font-mono font-bold {isDebit ? 'text-rose-400' : 'text-emerald-400'}">
                    {isDebit ? '-' : '+'}{tx.amount_coins}
                  </span>
                </td>
                <td>
                  <span class="font-mono text-xs text-slate-200">₹{tx.inr_equivalent}</span>
                </td>
                <td>
                  <span class="font-mono text-[11px] text-slate-400">
                    {tx.balance_before} &rarr; <strong class="text-slate-200">{tx.balance_after}</strong>
                  </span>
                </td>
                <td>
                  {#if tx.reference_type}
                    <span class="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-slate-300">
                      {tx.reference_type} #{tx.reference_id}
                    </span>
                  {:else}
                    <span class="text-slate-600">-</span>
                  {/if}
                </td>
                <td class="text-xs text-slate-300 max-w-xs truncate" title={tx.description}>
                  {tx.description}
                </td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>
  </div>
</div>
