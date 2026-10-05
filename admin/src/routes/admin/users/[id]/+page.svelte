<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { api } from '$lib/api';
  import { authState } from '$lib/auth.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import {
    ArrowLeft,
    Wallet,
    Coins,
    ShieldAlert,
    CheckCircle2,
    Calendar,
    Phone,
    Mail,
    Share2,
    AlertTriangle
  } from 'lucide-svelte';

  const userId = $derived(page.params.id);
  let user = $state<any>(null);
  let isLoading = $state(true);
  let errorMsg = $state('');

  // Suspend modal state
  let showSuspendModal = $state(false);
  let suspensionReason = $state('');
  let isUpdating = $state(false);

  async function loadUser() {
    isLoading = true;
    errorMsg = '';
    try {
      user = await api.get(`/admin/users/${userId}/`);
    } catch (err: any) {
      errorMsg = err.message || 'Failed to load user details.';
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadUser();
  });

  async function toggleSuspension() {
    isUpdating = true;
    try {
      const nextSuspendedState = !user.is_suspended;
      await api.patch(`/admin/users/${userId}/`, {
        is_suspended: nextSuspendedState,
        suspension_reason: nextSuspendedState ? suspensionReason.trim() : '',
        reason: nextSuspendedState
          ? `Account suspended: ${suspensionReason.trim()}`
          : 'Account reactivated by administrator.',
      });
      authState.showToast(
        nextSuspendedState ? 'User account has been suspended.' : 'User account reactivated.',
        'success'
      );
      showSuspendModal = false;
      suspensionReason = '';
      loadUser();
    } catch (err: any) {
      authState.showToast(err.message || 'Action failed.', 'error');
    } finally {
      isUpdating = false;
    }
  }
</script>

<div class="space-y-6 max-w-6xl">
  <!-- Back link -->
  <div>
    <a href="/admin/users" class="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white mb-3">
      <ArrowLeft size={14} />
      <span>Back to All Users</span>
    </a>

    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-white flex items-center gap-3">
          <span>{user?.full_name || 'User Profile'}</span>
          {#if user}
            <StatusBadge status={user.role.replace('_', ' ')} />
            {#if user.is_suspended}
              <StatusBadge status="SUSPENDED" />
            {/if}
          {/if}
        </h1>
        <p class="text-xs text-slate-400 font-mono mt-0.5">{user?.email}</p>
      </div>

      {#if user && authState.isFinanceAdmin}
        <div>
          {#if user.is_suspended}
            <button
              onclick={toggleSuspension}
              disabled={isUpdating}
              class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
            >
              Reactivate Account
            </button>
          {:else}
            <button
              onclick={() => (showSuspendModal = true)}
              class="px-3 py-1.5 rounded-lg bg-rose-950 hover:bg-rose-900 border border-rose-800 text-rose-300 text-xs font-semibold"
            >
              Suspend Account
            </button>
          {/if}
        </div>
      {/if}
    </div>
  </div>

  {#if isLoading}
    <div class="p-12 text-center text-xs text-slate-500">Loading user profile...</div>
  {:else if errorMsg}
    <div class="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-xs text-rose-300">{errorMsg}</div>
  {:else if user}
    <!-- Profile & Wallet Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Profile Card -->
      <div class="cbk-card p-6 space-y-3">
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Account Details</h3>
        <div class="text-xs space-y-2 text-slate-300">
          <div class="flex items-center gap-2">
            <Mail size={14} class="text-slate-500" />
            <span class="font-mono">{user.email}</span>
          </div>
          {#if user.phone_number}
            <div class="flex items-center gap-2">
              <Phone size={14} class="text-slate-500" />
              <span>{user.phone_number}</span>
            </div>
          {/if}
          <div class="flex items-center gap-2">
            <Share2 size={14} class="text-slate-500" />
            <span>Referral Code: <strong class="font-mono text-indigo-400">{user.referral_code}</strong></span>
          </div>
          <div class="flex items-center gap-2">
            <Calendar size={14} class="text-slate-500" />
            <span>Joined: {new Date(user.created_at).toLocaleString()}</span>
          </div>
        </div>
      </div>

      <!-- Wallet Card -->
      <div class="cbk-card p-6 bg-gradient-to-br from-slate-900 to-indigo-950/30 border-indigo-900/40">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-xs font-bold uppercase tracking-wider text-indigo-300">Wallet Balance</h3>
          <Wallet size={16} class="text-indigo-400" />
        </div>
        <div class="text-3xl font-black text-white font-mono">
          {(user.wallet_balance || 0).toLocaleString('en-IN')}
          <span class="text-xs font-sans text-indigo-300 font-medium ml-1">Coins</span>
        </div>
        <div class="mt-1 text-sm font-semibold text-amber-400">
          ≈ ₹{((user.wallet_balance || 0) / 10).toFixed(2)} INR
        </div>
        <div class="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 flex justify-between">
          <span>Lifetime Earned: {user.lifetime_earned?.toLocaleString()}</span>
          <span>Redeemed: {user.lifetime_redeemed?.toLocaleString()}</span>
        </div>
      </div>

      <!-- Activity Counter Stats -->
      <div class="cbk-card p-6">
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Platform Activity</h3>
        <div class="grid grid-cols-2 gap-3 text-center">
          <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
            <span class="block text-lg font-bold text-white">{user.stats?.total_clicks || 0}</span>
            <span class="text-[10px] text-slate-400 uppercase">Affiliate Clicks</span>
          </div>
          <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
            <span class="block text-lg font-bold text-white">{user.stats?.total_cashbacks || 0}</span>
            <span class="text-[10px] text-slate-400 uppercase">Cashback Orders</span>
          </div>
          <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
            <span class="block text-lg font-bold text-white">{user.stats?.total_redemptions || 0}</span>
            <span class="text-[10px] text-slate-400 uppercase">Withdrawals</span>
          </div>
          <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
            <span class="block text-lg font-bold text-white">{user.stats?.total_referrals || 0}</span>
            <span class="text-[10px] text-slate-400 uppercase">Friends Invited</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Coin Transactions Ledger -->
    <div class="cbk-card overflow-hidden">
      <div class="p-4 border-b border-slate-800 flex items-center justify-between">
        <h3 class="text-sm font-bold text-white">Recent Immutable Ledger Transactions</h3>
        <span class="text-[11px] text-slate-500 font-mono">Real-time audit history</span>
      </div>

      {#if !user.recent_transactions || user.recent_transactions.length === 0}
        <p class="p-6 text-center text-xs text-slate-500">No coin transactions recorded for this wallet yet.</p>
      {:else}
        <table class="cbk-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Amount</th>
              <th>Balance Before / After</th>
              <th>INR Equiv</th>
              <th>Description</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/80">
            {#each user.recent_transactions as tx}
              <tr>
                <td>
                  <StatusBadge status={tx.transaction_type} size="sm" />
                </td>
                <td>
                  <span class="font-mono font-bold {tx.transaction_type.includes('DEBIT') || tx.transaction_type === 'REDEMPTION' ? 'text-rose-400' : 'text-emerald-400'}">
                    {tx.transaction_type.includes('DEBIT') || tx.transaction_type === 'REDEMPTION' ? '-' : '+'}{tx.amount_coins}
                  </span>
                </td>
                <td class="font-mono text-xs text-slate-400">
                  {tx.balance_before} &rarr; {tx.balance_after}
                </td>
                <td class="font-mono text-xs text-slate-300">
                  ₹{tx.inr_equivalent}
                </td>
                <td class="text-xs text-slate-300 max-w-xs truncate">
                  {tx.description}
                </td>
                <td class="text-xs text-slate-400 font-mono">
                  {new Date(tx.created_at).toLocaleString()}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>
  {/if}
</div>

<!-- Suspend Confirmation Modal -->
{#if showSuspendModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
    <div class="bg-slate-900 border border-slate-700 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center gap-2 text-rose-400 font-bold text-sm">
        <AlertTriangle size={18} />
        <span>Suspend User Account</span>
      </div>
      <p class="text-xs text-slate-300">
        Suspended users cannot log in, earn cashback, or redeem wallet coins.
      </p>
      <div>
        <label for="suspensionReasonInput" class="block text-xs font-medium text-slate-300 mb-1">Mandatory Suspension Reason</label>
        <textarea
          id="suspensionReasonInput"
          bind:value={suspensionReason}
          rows={3}
          required
          placeholder="State reason for suspension (e.g. Terms violation, fraudulent referrals, suspicious activity)..."
          class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-rose-500"
        ></textarea>
      </div>
      <div class="flex items-center justify-end gap-3 pt-2">
        <button
          onclick={() => (showSuspendModal = false)}
          class="px-4 py-2 text-xs text-slate-400 hover:text-white"
        >
          Cancel
        </button>
        <button
          onclick={toggleSuspension}
          disabled={!suspensionReason.trim() || isUpdating}
          class="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold disabled:opacity-50"
        >
          Confirm Suspension
        </button>
      </div>
    </div>
  </div>
{/if}
