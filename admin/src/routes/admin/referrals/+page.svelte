<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Share2, RefreshCw, Search } from 'lucide-svelte';

  let referrals = $state<any[]>([]);
  let isLoading = $state(true);
  let search = $state('');

  async function loadReferrals() {
    isLoading = true;
    try {
      const res = await api.get('/admin/referrals/', { search });
      referrals = res.results || res;
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadReferrals();
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-white">Referral Network & Attribution</h1>
      <p class="text-xs text-slate-400 mt-1">Audit customer invite codes, qualified referral milestones, and bonus disbursements</p>
    </div>
    <button
      onclick={loadReferrals}
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
        oninput={loadReferrals}
        placeholder="Filter by referrer email, referred consumer, or code..."
        class="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
      />
    </div>
  </div>

  <div class="cbk-card overflow-hidden">
    <table class="cbk-table">
      <thead>
        <tr>
          <th>Referrer Account</th>
          <th>Invited Consumer</th>
          <th>Invite Code</th>
          <th>Bonus Coins</th>
          <th>Status</th>
          <th>Attribution Date</th>
          <th>Reward Disbursed</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800/80">
        {#if isLoading}
          <tr><td colspan="7" class="text-center py-8 text-xs text-slate-500">Loading referral trees...</td></tr>
        {:else if referrals.length === 0}
          <tr><td colspan="7" class="text-center py-8 text-xs text-slate-500">No referral records found.</td></tr>
        {:else}
          {#each referrals as ref}
            <tr>
              <td>
                <span class="text-xs font-mono text-indigo-300 font-semibold">{ref.referrer_email}</span>
              </td>
              <td>
                <span class="text-xs font-mono text-slate-300">{ref.referred_email}</span>
              </td>
              <td>
                <span class="font-mono text-xs font-bold text-amber-400">{ref.referral_code_used}</span>
              </td>
              <td>
                <span class="font-mono text-xs font-bold text-emerald-400">+{ref.reward_coins} Coins</span>
              </td>
              <td>
                <StatusBadge status={ref.status} size="sm" />
              </td>
              <td>
                <span class="text-xs text-slate-400 font-mono">{new Date(ref.created_at).toLocaleDateString()}</span>
              </td>
              <td>
                <span class="text-xs text-slate-400 font-mono">
                  {ref.rewarded_at ? new Date(ref.rewarded_at).toLocaleDateString() : 'Pending'}
                </span>
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>
