<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Search, Filter, RefreshCw, UserCheck, UserX, ExternalLink } from 'lucide-svelte';

  let users = $state<any[]>([]);
  let totalCount = $state(0);
  let isLoading = $state(true);
  let search = $state('');
  let roleFilter = $state('');
  let suspendedFilter = $state('');
  let currentPage = $state(1);

  async function loadUsers() {
    isLoading = true;
    try {
      const res = await api.get('/admin/users/', {
        search,
        role: roleFilter,
        is_suspended: suspendedFilter,
        page: currentPage,
      });
      users = res.results || res;
      totalCount = res.count || users.length;
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadUsers();
  });

  function handleSearch(e: SubmitEvent) {
    e.preventDefault();
    currentPage = 1;
    loadUsers();
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">User Accounts Directory</h1>
      <p class="text-xs text-slate-400 mt-1">Manage platform consumers, administrator privileges, and wallet statuses</p>
    </div>
    <button
      onclick={loadUsers}
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors"
    >
      <RefreshCw size={14} class={isLoading ? 'animate-spin' : ''} />
      <span>Refresh</span>
    </button>
  </div>

  <!-- Filters Toolbar -->
  <div class="cbk-card p-4 flex flex-wrap gap-4 items-center justify-between">
    <form onsubmit={handleSearch} class="flex items-center gap-2 flex-1 max-w-md">
      <div class="relative flex-1">
        <Search size={15} class="absolute left-3 top-2.5 text-slate-500" />
        <input
          type="text"
          bind:value={search}
          placeholder="Search by email, name, phone, or referral code..."
          class="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
        />
      </div>
      <button
        type="submit"
        class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium"
      >
        Search
      </button>
    </form>

    <div class="flex items-center gap-3">
      <select
        bind:value={roleFilter}
        onchange={loadUsers}
        class="bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 px-3 py-1.5 focus:outline-none"
      >
        <option value="">All Roles</option>
        <option value="CUSTOMER">Customer</option>
        <option value="SUPER_ADMIN">Super Admin</option>
        <option value="FINANCE_ADMIN">Finance Admin</option>
        <option value="OPERATIONS_ADMIN">Operations Admin</option>
      </select>

      <select
        bind:value={suspendedFilter}
        onchange={loadUsers}
        class="bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 px-3 py-1.5 focus:outline-none"
      >
        <option value="">All Statuses</option>
        <option value="false">Active Only</option>
        <option value="true">Suspended Only</option>
      </select>
    </div>
  </div>

  <!-- Users Table -->
  <div class="cbk-card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="cbk-table">
        <thead>
          <tr>
            <th>User</th>
            <th>Role</th>
            <th>Referral Code</th>
            <th>Coin Balance</th>
            <th>Lifetime Earned</th>
            <th>Status</th>
            <th>Joined Date</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/80">
          {#if isLoading}
            <tr>
              <td colspan="8" class="text-center py-8 text-xs text-slate-500">Loading accounts...</td>
            </tr>
          {:else if users.length === 0}
            <tr>
              <td colspan="8" class="text-center py-8 text-xs text-slate-500">No users found matching query.</td>
            </tr>
          {:else}
            {#each users as u}
              <tr>
                <td>
                  <div>
                    <span class="font-semibold text-slate-200">{u.full_name || 'Unnamed'}</span>
                    <span class="block text-[11px] text-slate-400 font-mono">{u.email}</span>
                  </div>
                </td>
                <td>
                  <StatusBadge status={u.role.replace('_', ' ')} size="sm" />
                </td>
                <td>
                  <span class="font-mono text-xs font-semibold text-indigo-400">{u.referral_code}</span>
                </td>
                <td>
                  <span class="font-mono text-xs font-bold text-amber-400">
                    {(u.wallet_balance || 0).toLocaleString('en-IN')} Coins
                  </span>
                  <span class="block text-[10px] text-slate-400">
                    ≈ ₹{((u.wallet_balance || 0) / 10).toFixed(2)}
                  </span>
                </td>
                <td>
                  <span class="font-mono text-xs text-slate-300">
                    {(u.lifetime_earned || 0).toLocaleString('en-IN')} Coins
                  </span>
                </td>
                <td>
                  {#if u.is_suspended}
                    <StatusBadge status="SUSPENDED" size="sm" />
                  {:else if u.is_active}
                    <StatusBadge status="ACTIVE" size="sm" />
                  {:else}
                    <StatusBadge status="INACTIVE" size="sm" />
                  {/if}
                </td>
                <td>
                  <span class="text-xs text-slate-400">
                    {new Date(u.created_at).toLocaleDateString()}
                  </span>
                </td>
                <td class="text-right">
                  <a
                    href="/admin/users/{u.id}"
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 text-xs font-medium transition-colors"
                  >
                    <span>Inspect</span>
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
</div>
