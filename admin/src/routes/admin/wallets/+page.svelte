<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { Wallet, Search, RefreshCw } from 'lucide-svelte';

  let wallets = $state<any[]>([]);
  let isLoading = $state(true);
  let search = $state('');

  async function loadWallets() {
    isLoading = true;
    try {
      const res = await api.get('/admin/wallets/', { search });
      wallets = res.results || res;
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadWallets();
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">Wallet Balances Directory</h1>
      <p class="text-xs text-slate-400 mt-1">Platform coin reserves, total balances, and lifetime issuance</p>
    </div>
    <button
      onclick={loadWallets}
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors"
    >
      <RefreshCw size={14} class={isLoading ? 'animate-spin' : ''} />
      <span>Refresh</span>
    </button>
  </div>

  <div class="cbk-card p-4">
    <div class="relative max-w-md">
      <Search size={15} class="absolute left-3 top-2.5 text-slate-500" />
      <input
        type="text"
        bind:value={search}
        oninput={loadWallets}
        placeholder="Filter by user email or name..."
        class="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
      />
    </div>
  </div>

  <div class="cbk-card overflow-hidden">
    <table class="cbk-table">
      <thead>
        <tr>
          <th>User Account</th>
          <th>Coin Balance</th>
          <th>INR Equivalent</th>
          <th>Lifetime Earned</th>
          <th>Lifetime Redeemed</th>
          <th>Lock Status</th>
          <th class="text-right">Action</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800/80">
        {#if isLoading}
          <tr><td colspan="7" class="text-center py-8 text-xs text-slate-500">Loading wallets...</td></tr>
        {:else if wallets.length === 0}
          <tr><td colspan="7" class="text-center py-8 text-xs text-slate-500">No wallets found.</td></tr>
        {:else}
          {#each wallets as w}
            <tr>
              <td>
                <span class="font-semibold text-slate-200">{w.user_name || 'User'}</span>
                <span class="block text-[11px] font-mono text-slate-400">{w.user_email}</span>
              </td>
              <td>
                <span class="font-mono text-xs font-bold text-amber-400">
                  {w.coin_balance.toLocaleString('en-IN')} Coins
                </span>
              </td>
              <td>
                <span class="font-mono text-xs font-semibold text-emerald-400">
                  ₹{w.inr_value} INR
                </span>
              </td>
              <td>
                <span class="font-mono text-xs text-slate-300">
                  {w.lifetime_earned.toLocaleString('en-IN')} Coins
                </span>
              </td>
              <td>
                <span class="font-mono text-xs text-slate-400">
                  {w.lifetime_redeemed.toLocaleString('en-IN')} Coins
                </span>
              </td>
              <td>
                {#if w.is_locked}
                  <span class="px-2 py-0.5 text-xs rounded bg-rose-950 text-rose-300 border border-rose-800 font-semibold">Locked</span>
                {:else}
                  <span class="px-2 py-0.5 text-xs rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">Active</span>
                {/if}
              </td>
              <td class="text-right">
                <a href="/admin/users/{w.user}" class="text-xs text-indigo-400 hover:text-indigo-300 font-medium">
                  View Profile &rarr;
                </a>
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>
