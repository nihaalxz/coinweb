<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Store, Plus, ExternalLink, RefreshCw, Search } from 'lucide-svelte';

  let merchants = $state<any[]>([]);
  let isLoading = $state(true);
  let search = $state('');
  let categoryFilter = $state('');

  const categories = [
    'marketplaces',
    'fashion',
    'electronics',
    'travel',
    'beauty',
    'grocery',
    'other'
  ];

  async function loadMerchants() {
    isLoading = true;
    try {
      const res = await api.get('/admin/merchants/', {
        search,
        category: categoryFilter,
      });
      merchants = res.results || res;
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadMerchants();
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">Partner Merchants & Stores</h1>
      <p class="text-xs text-slate-400 mt-1">Configure affiliate merchant rates, tracking URLs, and customer reward percentages</p>
    </div>
    <div class="flex items-center gap-3">
      <button
        onclick={loadMerchants}
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors"
      >
        <RefreshCw size={14} class={isLoading ? 'animate-spin' : ''} />
        <span>Refresh</span>
      </button>
      <a
        href="/admin/merchants/new"
        class="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30"
      >
        <Plus size={15} />
        <span>Add Merchant</span>
      </a>
    </div>
  </div>

  <!-- Filters -->
  <div class="cbk-card p-4 flex flex-wrap gap-4 items-center justify-between">
    <div class="relative flex-1 max-w-md">
      <Search size={15} class="absolute left-3 top-2.5 text-slate-500" />
      <input
        type="text"
        bind:value={search}
        oninput={loadMerchants}
        placeholder="Filter merchants by name or slug..."
        class="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
      />
    </div>

    <select
      bind:value={categoryFilter}
      onchange={loadMerchants}
      class="bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 px-3 py-1.5 focus:outline-none"
    >
      <option value="">All Categories</option>
      {#each categories as cat}
        <option value={cat}>{cat.toUpperCase()}</option>
      {/each}
    </select>
  </div>

  <!-- Merchants Grid/Table -->
  <div class="cbk-card overflow-hidden">
    <table class="cbk-table">
      <thead>
        <tr>
          <th>Store Name</th>
          <th>Category</th>
          <th>CBK Commission</th>
          <th>Customer Cashback</th>
          <th>Badge</th>
          <th>Affiliate Clicks</th>
          <th>Orders</th>
          <th>Status</th>
          <th class="text-right">Action</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800/80">
        {#if isLoading}
          <tr><td colspan="9" class="text-center py-8 text-xs text-slate-500">Loading merchants...</td></tr>
        {:else if merchants.length === 0}
          <tr><td colspan="9" class="text-center py-8 text-xs text-slate-500">No merchants found.</td></tr>
        {:else}
          {#each merchants as m}
            <tr>
              <td>
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300">
                    {m.name.substring(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <span class="font-bold text-slate-200">{m.name}</span>
                    <span class="block text-[10px] font-mono text-slate-400">{m.slug}</span>
                  </div>
                </div>
              </td>
              <td>
                <span class="text-xs uppercase font-medium text-slate-400 tracking-wider">{m.category}</span>
              </td>
              <td>
                <span class="font-mono text-xs font-semibold text-slate-300">{m.commission_rate}%</span>
              </td>
              <td>
                <span class="font-mono text-xs font-bold text-amber-400">{m.cbk_reward_rate}%</span>
              </td>
              <td>
                {#if m.reward_badge}
                  <span class="px-2 py-0.5 rounded bg-indigo-950/70 border border-indigo-800/60 text-[10px] font-bold text-indigo-300">
                    {m.reward_badge}
                  </span>
                {:else}
                  <span class="text-slate-600">-</span>
                {/if}
              </td>
              <td>
                <span class="font-mono text-xs text-slate-300">{m.clicks_count || 0}</span>
              </td>
              <td>
                <span class="font-mono text-xs font-semibold text-emerald-400">{m.conversions_count || 0}</span>
              </td>
              <td>
                {#if m.is_active}
                  <StatusBadge status="ACTIVE" size="sm" />
                {:else}
                  <StatusBadge status="INACTIVE" size="sm" />
                {/if}
              </td>
              <td class="text-right">
                <a
                  href={m.website_url}
                  target="_blank"
                  rel="noreferrer"
                  class="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-white"
                >
                  <span>Visit</span>
                  <ExternalLink size={12} />
                </a>
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>
