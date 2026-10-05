<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { ShieldAlert, RefreshCw, Search } from 'lucide-svelte';

  let logs = $state<any[]>([]);
  let isLoading = $state(true);
  let search = $state('');
  let actionFilter = $state('');

  async function loadLogs() {
    isLoading = true;
    try {
      const res = await api.get('/admin/audit-logs/', {
        search,
        action: actionFilter,
      });
      logs = res.results || res;
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadLogs();
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">Immutable Administrative Audit Logs</h1>
      <p class="text-xs text-slate-400 mt-1">Non-repudiable audit trail of all sensitive operations, coin adjustments, and permission changes</p>
    </div>
    <button
      onclick={loadLogs}
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors"
    >
      <RefreshCw size={14} class={isLoading ? 'animate-spin' : ''} />
      <span>Refresh</span>
    </button>
  </div>

  <div class="cbk-card p-4 flex flex-wrap gap-4 items-center justify-between">
    <div class="relative flex-1 max-w-md">
      <Search size={15} class="absolute left-3 top-2.5 text-slate-500" />
      <input
        type="text"
        bind:value={search}
        oninput={loadLogs}
        placeholder="Filter by audit reason or entity ID..."
        class="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
      />
    </div>

    <select
      bind:value={actionFilter}
      onchange={loadLogs}
      class="bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 px-3 py-1.5 focus:outline-none"
    >
      <option value="">All Administrative Actions</option>
      <option value="MANUAL_COIN_CREDIT">Manual Coin Credit</option>
      <option value="MANUAL_COIN_DEBIT">Manual Coin Debit</option>
      <option value="CASHBACK_STATUS_CHANGE">Cashback Status Change</option>
      <option value="REDEMPTION_STATUS_CHANGE">Redemption Status Change</option>
      <option value="USER_SUSPENSION">User Suspension</option>
      <option value="USER_REACTIVATION">User Reactivation</option>
      <option value="ROLE_CHANGE">Role Change</option>
      <option value="MERCHANT_UPDATED">Merchant Update</option>
    </select>
  </div>

  <div class="cbk-card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="cbk-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Administrator</th>
            <th>Action</th>
            <th>Target Entity</th>
            <th>Reason / Justification</th>
            <th>IP Address</th>
            <th>Diff Summary</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/80">
          {#if isLoading}
            <tr><td colspan="7" class="text-center py-8 text-xs text-slate-500">Loading audit trail...</td></tr>
          {:else if logs.length === 0}
            <tr><td colspan="7" class="text-center py-8 text-xs text-slate-500">No audit events recorded yet.</td></tr>
          {:else}
            {#each logs as log}
              <tr>
                <td>
                  <span class="font-mono text-xs text-slate-300">{new Date(log.created_at).toLocaleString()}</span>
                </td>
                <td>
                  <span class="text-xs font-mono text-indigo-300 font-semibold">{log.admin_email}</span>
                </td>
                <td>
                  <StatusBadge status={log.action} size="sm" />
                </td>
                <td>
                  <span class="text-xs font-mono text-slate-300">{log.entity} #{log.entity_id}</span>
                </td>
                <td class="text-xs text-slate-200 max-w-sm">
                  {log.reason || 'System operation'}
                </td>
                <td>
                  <span class="font-mono text-[11px] text-slate-400">{log.ip_address || '127.0.0.1'}</span>
                </td>
                <td>
                  <div class="text-[11px] font-mono text-slate-400 max-w-xs truncate" title={JSON.stringify(log.new_values)}>
                    {JSON.stringify(log.new_values)}
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
