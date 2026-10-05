<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { authState } from '$lib/auth.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { ArrowDownToLine, Search, RefreshCw, CheckCircle2, XCircle, Clock, AlertTriangle } from 'lucide-svelte';

  let redemptions = $state<any[]>([]);
  let isLoading = $state(true);
  let search = $state('');
  let statusFilter = $state('');

  // Action Modal
  let showActionModal = $state(false);
  let selectedRedemption = $state<any>(null);
  let actionTargetStatus = $state<'PROCESSING' | 'COMPLETED' | 'FAILED'>('COMPLETED');
  let utrNumber = $state('');
  let actionReason = $state('');
  let isUpdating = $state(false);
  let modalError = $state('');

  async function loadRedemptions() {
    isLoading = true;
    try {
      const res = await api.get('/admin/redemptions/', {
        search,
        status: statusFilter,
      });
      redemptions = res.results || res;
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadRedemptions();
  });

  function openAction(item: any, target: 'PROCESSING' | 'COMPLETED' | 'FAILED') {
    selectedRedemption = item;
    actionTargetStatus = target;
    utrNumber = item.utr_number || '';
    actionReason = '';
    modalError = '';
    showActionModal = true;
  }

  async function executeAction() {
    if (!selectedRedemption) return;
    modalError = '';

    if (actionTargetStatus === 'COMPLETED' && !utrNumber.trim()) {
      modalError = 'UTR / Bank Settlement Reference number is required.';
      return;
    }
    if (actionTargetStatus === 'FAILED' && !actionReason.trim()) {
      modalError = 'A failure reason is mandatory for refunding coins.';
      return;
    }

    isUpdating = true;
    try {
      await api.post(`/admin/redemptions/${selectedRedemption.redemption_id}/transition/`, {
        status: actionTargetStatus,
        utr_number: utrNumber.trim(),
        reason: actionReason.trim(),
      });
      authState.showToast(
        `Redemption ${selectedRedemption.redemption_id.substring(0, 8)} updated to ${actionTargetStatus}.`,
        'success'
      );
      showActionModal = false;
      loadRedemptions();
    } catch (err: any) {
      modalError = err.message || 'Action failed.';
    } finally {
      isUpdating = false;
    }
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">Redemption Payout Operations</h1>
      <p class="text-xs text-slate-400 mt-1">Review UPI and direct bank withdrawal requests, verify payouts, and disburse settlements</p>
    </div>
    <button
      onclick={loadRedemptions}
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
        oninput={loadRedemptions}
        placeholder="Search by Redemption ID, consumer email, or UTR..."
        class="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
      />
    </div>

    <select
      bind:value={statusFilter}
      onchange={loadRedemptions}
      class="bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 px-3 py-1.5 focus:outline-none"
    >
      <option value="">All Statuses</option>
      <option value="REQUESTED">Requested (Action Required)</option>
      <option value="PROCESSING">Processing</option>
      <option value="COMPLETED">Completed</option>
      <option value="FAILED">Failed / Refunded</option>
    </select>
  </div>

  <!-- Redemptions Table -->
  <div class="cbk-card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="cbk-table">
        <thead>
          <tr>
            <th>Payout Ref / Time</th>
            <th>Consumer</th>
            <th>Method</th>
            <th>Masked Account / VPA</th>
            <th>Coins Debited</th>
            <th>Payout Amount</th>
            <th>UTR Ref</th>
            <th>Status</th>
            <th class="text-right">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/80">
          {#if isLoading}
            <tr><td colspan="9" class="text-center py-8 text-xs text-slate-500">Loading redemptions...</td></tr>
          {:else if redemptions.length === 0}
            <tr><td colspan="9" class="text-center py-8 text-xs text-slate-500">No redemptions found.</td></tr>
          {:else}
            {#each redemptions as r}
              <tr>
                <td>
                  <span class="font-mono text-xs font-semibold text-indigo-400">{r.redemption_id.substring(0, 8)}...</span>
                  <span class="block text-[10px] text-slate-400 font-mono">{new Date(r.requested_at).toLocaleString()}</span>
                </td>
                <td>
                  <span class="text-xs font-mono text-slate-300">{r.user_email}</span>
                </td>
                <td>
                  <span class="px-2 py-0.5 rounded bg-slate-800 text-[11px] font-bold text-slate-300">{r.payout_method}</span>
                </td>
                <td>
                  <span class="font-mono text-xs text-slate-300">{r.masked_identifier}</span>
                </td>
                <td>
                  <span class="font-mono text-xs font-bold text-amber-400">{r.coins_deducted} Coins</span>
                </td>
                <td>
                  <span class="font-mono text-xs font-bold text-emerald-400">₹{r.inr_amount} INR</span>
                </td>
                <td>
                  {#if r.utr_number}
                    <span class="font-mono text-xs text-indigo-300 bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-800/60">
                      {r.utr_number}
                    </span>
                  {:else}
                    <span class="text-slate-600 font-mono text-xs">-</span>
                  {/if}
                </td>
                <td>
                  <StatusBadge status={r.status} size="sm" />
                </td>
                <td class="text-right">
                  <div class="inline-flex items-center gap-1.5">
                    {#if r.status === 'REQUESTED'}
                      <button
                        onclick={() => openAction(r, 'PROCESSING')}
                        class="px-2 py-1 rounded bg-amber-950/80 hover:bg-amber-900 border border-amber-800 text-amber-300 text-xs font-medium"
                      >
                        Process
                      </button>
                      <button
                        onclick={() => openAction(r, 'COMPLETED')}
                        class="px-2 py-1 rounded bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-800 text-emerald-300 text-xs font-medium"
                      >
                        Complete
                      </button>
                      <button
                        onclick={() => openAction(r, 'FAILED')}
                        class="px-2 py-1 rounded bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-300 text-xs font-medium"
                      >
                        Fail
                      </button>
                    {:else if r.status === 'PROCESSING'}
                      <button
                        onclick={() => openAction(r, 'COMPLETED')}
                        class="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                      >
                        Settle UTR
                      </button>
                      <button
                        onclick={() => openAction(r, 'FAILED')}
                        class="px-2 py-1 rounded bg-rose-950 hover:bg-rose-900 border border-rose-800 text-rose-300 text-xs font-medium"
                      >
                        Fail
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

<!-- Action Modal -->
{#if showActionModal && selectedRedemption}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
    <div class="bg-slate-900 border border-slate-700 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 class="text-sm font-bold text-white">Disburse Payout #{selectedRedemption.redemption_id.substring(0, 8)}</h3>
        <StatusBadge status={actionTargetStatus} size="sm" />
      </div>

      {#if modalError}
        <div class="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-xs text-rose-300 flex items-start gap-2">
          <AlertTriangle size={15} class="text-rose-400 shrink-0 mt-0.5" />
          <span>{modalError}</span>
        </div>
      {/if}

      <div class="p-3 rounded-lg bg-slate-800/80 text-xs space-y-1 text-slate-300">
        <div>Beneficiary: <strong class="font-mono text-white">{selectedRedemption.user_email}</strong></div>
        <div>Method: <strong class="text-white">{selectedRedemption.payout_method}</strong> ({selectedRedemption.masked_identifier})</div>
        <div>Settlement Amount: <strong class="font-mono text-emerald-400">₹{selectedRedemption.inr_amount} INR</strong> ({selectedRedemption.coins_deducted} Coins)</div>
      </div>

      {#if actionTargetStatus === 'COMPLETED'}
        <div>
          <label for="payoutUtrNumber" class="block text-xs font-semibold text-slate-300 mb-1">
            Bank Settlement Reference / UTR Number <span class="text-rose-400">*</span>
          </label>
          <input
            id="payoutUtrNumber"
            type="text"
            bind:value={utrNumber}
            required
            placeholder="e.g. UTR202609121092837"
            class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
          />
        </div>
      {:else if actionTargetStatus === 'FAILED'}
        <div class="p-3 rounded-lg bg-rose-950/40 border border-rose-900/60 text-[11px] text-rose-300">
          Marking as FAILED will automatically refund <strong>{selectedRedemption.coins_deducted} CBK Coins</strong> back to the consumer's wallet ledger.
        </div>
        <div>
          <label for="payoutFailReason" class="block text-xs font-semibold text-slate-300 mb-1">
            Mandatory Failure Reason <span class="text-rose-400">*</span>
          </label>
          <textarea
            id="payoutFailReason"
            bind:value={actionReason}
            rows={2}
            required
            placeholder="e.g. Beneficiary UPI VPA does not exist or was rejected by receiving bank..."
            class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-rose-500"
          ></textarea>
        </div>
      {/if}

      <div class="flex items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onclick={() => (showActionModal = false)}
          class="px-4 py-2 text-xs text-slate-400 hover:text-white"
        >
          Cancel
        </button>
        <button
          type="button"
          onclick={executeAction}
          disabled={isUpdating}
          class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg disabled:opacity-50"
        >
          {isUpdating ? 'Saving...' : `Confirm ${actionTargetStatus}`}
        </button>
      </div>
    </div>
  </div>
{/if}
