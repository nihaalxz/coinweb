<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { authState } from '$lib/auth.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Coins, Search, RefreshCw, Check, X, RotateCcw, AlertCircle } from 'lucide-svelte';

  let cashbacks = $state<any[]>([]);
  let isLoading = $state(true);
  let search = $state('');
  let statusFilter = $state('');

  // Transition Dialog
  let showTransitionModal = $state(false);
  let selectedCashback = $state<any>(null);
  let targetStatus = $state<'APPROVED' | 'REJECTED' | 'REVERSED'>('APPROVED');
  let transitionReason = $state('');
  let isUpdating = $state(false);
  let modalError = $state('');

  async function loadCashbacks() {
    isLoading = true;
    try {
      const res = await api.get('/admin/cashback/', {
        search,
        status: statusFilter,
      });
      cashbacks = res.results || res;
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadCashbacks();
  });

  function openTransition(item: any, status: 'APPROVED' | 'REJECTED' | 'REVERSED') {
    selectedCashback = item;
    targetStatus = status;
    transitionReason = status === 'APPROVED' ? 'Merchant affiliate network validated conversion.' : '';
    modalError = '';
    showTransitionModal = true;
  }

  async function executeTransition() {
    if (!selectedCashback) return;
    modalError = '';
    isUpdating = true;

    try {
      await api.post(`/admin/cashback/${selectedCashback.id}/transition/`, {
        status: targetStatus,
        reason: transitionReason.trim(),
      });
      authState.showToast(`Cashback #${selectedCashback.id} transitioned to ${targetStatus}.`, 'success');
      showTransitionModal = false;
      loadCashbacks();
    } catch (err: any) {
      modalError = err.message || 'Status transition failed.';
    } finally {
      isUpdating = false;
    }
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">Cashback Reconciliation & Claims</h1>
      <p class="text-xs text-slate-400 mt-1">Audit merchant transactions, approve verified coin disbursements, and handle order reversals</p>
    </div>
    <button
      onclick={loadCashbacks}
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors"
    >
      <RefreshCw size={14} class={isLoading ? 'animate-spin' : ''} />
      <span>Refresh</span>
    </button>
  </div>

  <!-- Filters -->
  <div class="cbk-card p-4 flex flex-wrap gap-4 items-center justify-between">
    <div class="relative flex-1 max-w-md">
      <Search size={15} class="absolute left-3 top-2.5 text-slate-500" />
      <input
        type="text"
        bind:value={search}
        oninput={loadCashbacks}
        placeholder="Search by Order ID, merchant, or user email..."
        class="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
      />
    </div>

    <div class="flex items-center gap-2">
      <select
        bind:value={statusFilter}
        onchange={loadCashbacks}
        class="bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 px-3 py-1.5 focus:outline-none"
      >
        <option value="">All Statuses</option>
        <option value="PENDING">Pending Only</option>
        <option value="APPROVED">Approved Only</option>
        <option value="REJECTED">Rejected Only</option>
        <option value="REVERSED">Reversed Only</option>
      </select>
    </div>
  </div>

  <!-- Cashback Table -->
  <div class="cbk-card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="cbk-table">
        <thead>
          <tr>
            <th>Order Ref / Date</th>
            <th>Consumer</th>
            <th>Merchant</th>
            <th>Order Total</th>
            <th>Cashback INR</th>
            <th>CBK Coins</th>
            <th>Status</th>
            <th class="text-right">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/80">
          {#if isLoading}
            <tr><td colspan="8" class="text-center py-8 text-xs text-slate-500">Loading cashback records...</td></tr>
          {:else if cashbacks.length === 0}
            <tr><td colspan="8" class="text-center py-8 text-xs text-slate-500">No cashback records found.</td></tr>
          {:else}
            {#each cashbacks as cb}
              <tr>
                <td>
                  <span class="font-mono text-xs font-bold text-slate-200">{cb.order_id}</span>
                  <span class="block text-[10px] text-slate-400 font-mono">{new Date(cb.created_at).toLocaleDateString()}</span>
                </td>
                <td>
                  <span class="text-xs font-mono text-slate-300">{cb.user_email}</span>
                </td>
                <td>
                  <span class="font-semibold text-slate-200">{cb.merchant_name}</span>
                </td>
                <td>
                  <span class="font-mono text-xs text-slate-300">₹{cb.order_amount}</span>
                </td>
                <td>
                  <span class="font-mono text-xs font-semibold text-emerald-400">₹{cb.cashback_inr}</span>
                </td>
                <td>
                  <span class="font-mono text-xs font-bold text-amber-400">{cb.cbk_coins} Coins</span>
                </td>
                <td>
                  <StatusBadge status={cb.status} size="sm" />
                </td>
                <td class="text-right">
                  <div class="inline-flex items-center gap-1.5">
                    {#if cb.status === 'PENDING'}
                      <button
                        onclick={() => openTransition(cb, 'APPROVED')}
                        title="Approve & Credit Coins"
                        class="p-1 rounded bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-800 text-emerald-400"
                      >
                        <Check size={14} />
                      </button>
                      <button
                        onclick={() => openTransition(cb, 'REJECTED')}
                        title="Reject Claim"
                        class="p-1 rounded bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-400"
                      >
                        <X size={14} />
                      </button>
                    {:else if cb.status === 'APPROVED'}
                      <button
                        onclick={() => openTransition(cb, 'REVERSED')}
                        title="Reverse Cashback (Customer Return)"
                        class="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-amber-400 border border-slate-700"
                      >
                        <RotateCcw size={14} />
                      </button>
                    {:else}
                      <span class="text-[11px] text-slate-600 font-mono">Terminal</span>
                    {/if}
                  </div>
                </td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- Status Transition Modal -->
{#if showTransitionModal && selectedCashback}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
    <div class="bg-slate-900 border border-slate-700 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 class="text-sm font-bold text-white">Transition Cashback #{selectedCashback.id}</h3>
        <StatusBadge status={targetStatus} size="sm" />
      </div>

      {#if modalError}
        <div class="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-xs text-rose-300 flex items-start gap-2">
          <AlertCircle size={15} class="text-rose-400 shrink-0 mt-0.5" />
          <span>{modalError}</span>
        </div>
      {/if}

      <div class="p-3 rounded-lg bg-slate-800/80 text-xs space-y-1 text-slate-300">
        <div>Merchant: <strong>{selectedCashback.merchant_name}</strong></div>
        <div>Order: <strong class="font-mono">{selectedCashback.order_id}</strong></div>
        <div>Coins Impact: <strong class="font-mono text-amber-400">{selectedCashback.cbk_coins} Coins</strong> (₹{selectedCashback.cashback_inr})</div>
      </div>

      {#if targetStatus === 'APPROVED'}
        <p class="text-[11px] text-emerald-400/90 leading-relaxed">
          Confirming will atomically credit <strong>{selectedCashback.cbk_coins} CBK Coins</strong> to the consumer's wallet ledger.
        </p>
      {:else if targetStatus === 'REVERSED'}
        <p class="text-[11px] text-amber-400/90 leading-relaxed">
          Reversal will atomically debit <strong>{selectedCashback.cbk_coins} CBK Coins</strong> from the consumer's wallet with an audit ledger entry.
        </p>
      {/if}

      <div>
        <label for="cashbackTransitionReason" class="block text-xs font-medium text-slate-300 mb-1">Mandatory Audit Reason / Notes</label>
        <textarea
          id="cashbackTransitionReason"
          bind:value={transitionReason}
          rows={3}
          required
          placeholder="State network confirmation reference or return tracking..."
          class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
        ></textarea>
      </div>

      <div class="flex items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onclick={() => (showTransitionModal = false)}
          class="px-4 py-2 text-xs text-slate-400 hover:text-white"
        >
          Cancel
        </button>
        <button
          type="button"
          onclick={executeTransition}
          disabled={isUpdating}
          class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg disabled:opacity-50"
        >
          {isUpdating ? 'Applying...' : `Confirm ${targetStatus}`}
        </button>
      </div>
    </div>
  </div>
{/if}
