<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Sparkles, Plus, RefreshCw } from 'lucide-svelte';

  let promotions = $state<any[]>([]);
  let isLoading = $state(true);

  async function loadPromotions() {
    isLoading = true;
    try {
      const res = await api.get('/admin/promotions/');
      promotions = res.results || res;
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadPromotions();
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">Promotional Campaigns</h1>
      <p class="text-xs text-slate-400 mt-1">Configure seasonal events, reward multipliers, and bonus coin boost campaigns</p>
    </div>
    <div class="flex items-center gap-3">
      <button
        onclick={loadPromotions}
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors"
      >
        <RefreshCw size={14} class={isLoading ? 'animate-spin' : ''} />
        <span>Refresh</span>
      </button>
      <a
        href="/admin/promotions/new"
        class="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30"
      >
        <Plus size={15} />
        <span>New Campaign</span>
      </a>
    </div>
  </div>

  <div class="cbk-card overflow-hidden">
    <table class="cbk-table">
      <thead>
        <tr>
          <th>Campaign Title</th>
          <th>Multiplier</th>
          <th>Bonus Coins</th>
          <th>Start Date</th>
          <th>End Date</th>
          <th>Running Status</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800/80">
        {#if isLoading}
          <tr><td colspan="7" class="text-center py-8 text-xs text-slate-500">Loading campaigns...</td></tr>
        {:else if promotions.length === 0}
          <tr><td colspan="7" class="text-center py-8 text-xs text-slate-500">No campaigns created yet.</td></tr>
        {:else}
          {#each promotions as p}
            <tr>
              <td>
                <span class="font-bold text-slate-200">{p.title}</span>
                <span class="block text-[11px] text-slate-400">{p.description}</span>
              </td>
              <td>
                <span class="font-mono text-xs font-bold text-indigo-400">{p.cashback_multiplier}x</span>
              </td>
              <td>
                <span class="font-mono text-xs font-bold text-amber-400">+{p.bonus_coins} Coins</span>
              </td>
              <td>
                <span class="text-xs text-slate-300 font-mono">{new Date(p.start_date).toLocaleDateString()}</span>
              </td>
              <td>
                <span class="text-xs text-slate-300 font-mono">{new Date(p.end_date).toLocaleDateString()}</span>
              </td>
              <td>
                {#if p.is_running}
                  <span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-[11px] font-bold">LIVE NOW</span>
                {:else}
                  <span class="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[11px]">SCHEDULED / EXPIRED</span>
                {/if}
              </td>
              <td>
                {#if p.is_active}
                  <StatusBadge status="ACTIVE" size="sm" />
                {:else}
                  <StatusBadge status="INACTIVE" size="sm" />
                {/if}
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>
