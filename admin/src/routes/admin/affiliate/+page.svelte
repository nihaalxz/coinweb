<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { MousePointerClick, RefreshCw, Search } from 'lucide-svelte';

  let clicks = $state<any[]>([]);
  let isLoading = $state(true);
  let search = $state('');

  async function loadClicks() {
    isLoading = true;
    try {
      const res = await api.get('/admin/affiliate-clicks/', { search });
      clicks = res.results || res;
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadClicks();
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">Affiliate Click Telemetry</h1>
      <p class="text-xs text-slate-400 mt-1">Real-time tracking of customer click-outs to external merchant stores</p>
    </div>
    <button
      onclick={loadClicks}
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
        oninput={loadClicks}
        placeholder="Filter by Click ID, merchant, or user email..."
        class="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
      />
    </div>
  </div>

  <div class="cbk-card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="cbk-table">
        <thead>
          <tr>
            <th>Click ID / Time</th>
            <th>Consumer</th>
            <th>Target Merchant</th>
            <th>Source / Campaign</th>
            <th>Attribution IP</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/80">
          {#if isLoading}
            <tr><td colspan="6" class="text-center py-8 text-xs text-slate-500">Loading click telemetry...</td></tr>
          {:else if clicks.length === 0}
            <tr><td colspan="6" class="text-center py-8 text-xs text-slate-500">No clicks recorded yet.</td></tr>
          {:else}
            {#each clicks as c}
              <tr>
                <td>
                  <span class="font-mono text-xs text-indigo-400 font-semibold">{c.click_id.substring(0, 8)}...</span>
                  <span class="block text-[10px] text-slate-400 font-mono">{new Date(c.created_at).toLocaleString()}</span>
                </td>
                <td>
                  <span class="text-xs font-mono text-slate-300">{c.user_email}</span>
                </td>
                <td>
                  <span class="font-semibold text-slate-200">{c.merchant_name}</span>
                </td>
                <td>
                  <span class="text-xs text-slate-300 font-mono">{c.source}</span>
                  {#if c.campaign}
                    <span class="block text-[10px] text-indigo-400 font-mono">{c.campaign}</span>
                  {/if}
                </td>
                <td>
                  <span class="text-xs text-slate-400 font-mono">{c.ip_address || '127.0.0.1'}</span>
                </td>
                <td>
                  <StatusBadge status={c.status} size="sm" />
                </td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>
  </div>
</div>
