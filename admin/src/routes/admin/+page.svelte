<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import MetricCard from '$lib/components/MetricCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import {
    Users,
    Wallet,
    Receipt,
    Coins,
    ArrowDownToLine,
    MousePointerClick,
    Store,
    Share2,
    RefreshCw,
    TrendingUp
  } from 'lucide-svelte';

  let metrics = $state<any>(null);
  let isLoading = $state(true);
  let errorMsg = $state('');

  async function loadMetrics() {
    isLoading = true;
    errorMsg = '';
    try {
      metrics = await api.get('/admin/dashboard/metrics/');
    } catch (err: any) {
      errorMsg = err.message || 'Failed to load dashboard metrics.';
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadMetrics();
  });

  function formatNum(val: number | string): string {
    if (val === undefined || val === null) return '0';
    return Number(val).toLocaleString('en-IN');
  }

  function formatINR(val: number | string): string {
    if (val === undefined || val === null) return '₹0.00';
    return '₹' + Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
</script>

<div class="space-y-8">
  <!-- Page Header -->
  <div class="flex items-center justify-between pb-2">
    <div>
      <h1 class="text-xl font-bold tracking-tight text-white">Operations & Financial Overview</h1>
      <p class="text-xs text-slate-400 mt-1">Real-time ledger audit, transaction volume, and platform performance</p>
    </div>
    <button
      onclick={loadMetrics}
      disabled={isLoading}
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors disabled:opacity-50"
    >
      <RefreshCw size={14} class={isLoading ? 'animate-spin' : ''} />
      <span>Refresh Data</span>
    </button>
  </div>

  {#if errorMsg}
    <div class="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-xs text-rose-300">
      {errorMsg}
    </div>
  {/if}

  {#if isLoading}
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 animate-pulse">
      {#each Array(8) as _}
        <div class="h-28 rounded-xl bg-slate-800/50"></div>
      {/each}
    </div>
  {:else if metrics}
    <!-- SECTION 1: FINANCIAL LEDGER ACCRUAL METRICS -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">CBK Coin & Monetary Accrual</h2>
        <span class="text-[11px] font-mono text-amber-400/90 font-medium">Peg Rule: 10 Coins = ₹1 INR</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Coins Outstanding"
          value={formatNum(metrics.wallet.coins_outstanding)}
          subtext={`Cash Reserve: ${formatINR(metrics.wallet.inr_outstanding)}`}
          icon={Wallet}
        />
        <MetricCard
          title="Total Lifetime Issued"
          value={formatNum(metrics.wallet.coins_issued)}
          subtext={`Gross Rewards: ${formatINR(metrics.wallet.inr_issued)}`}
          icon={Coins}
        />
        <MetricCard
          title="Total Payouts Settled"
          value={formatINR(metrics.redemptions.total_payout_inr)}
          subtext={`${formatNum(metrics.wallet.coins_redeemed)} coins redeemed`}
          icon={ArrowDownToLine}
        />
        <MetricCard
          title="Pending Withdrawals"
          value={metrics.redemptions.requested}
          subtext={`${metrics.redemptions.processing} currently processing`}
          trend={metrics.redemptions.requested > 0 ? 'Requires Action' : 'Cleared'}
          trendPositive={metrics.redemptions.requested === 0}
          icon={Receipt}
        />
      </div>
    </div>

    <!-- SECTION 2: PLATFORM & COMMERCE METRICS -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">Commerce & Customer Activity</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Registered Consumers"
          value={formatNum(metrics.users.total)}
          subtext={`${metrics.users.active} active accounts`}
          icon={Users}
        />
        <MetricCard
          title="Approved Cashback Value"
          value={formatINR(metrics.cashback.approved_inr)}
          subtext={`${metrics.cashback.approved} verified transactions`}
          icon={TrendingUp}
        />
        <MetricCard
          title="Affiliate Click-Throughs"
          value={formatNum(metrics.affiliate.total_clicks)}
          subtext={`${metrics.affiliate.conversion_rate_percent}% conversion rate`}
          icon={MousePointerClick}
        />
        <MetricCard
          title="Active Partner Merchants"
          value={metrics.merchants.active_count}
          subtext="Verified store integrations"
          icon={Store}
        />
      </div>
    </div>

    <!-- SECTION 3: RECENT CONVERSION & TOP STORES -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Cashback Pipeline Breakdown -->
      <div class="cbk-card p-6">
        <h3 class="text-sm font-bold text-white mb-4">Cashback Verification Pipeline</h3>
        <div class="space-y-3">
          <div class="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div class="flex items-center gap-3">
              <StatusBadge status="PENDING" />
              <span class="text-xs text-slate-300">Pending Reconciliation</span>
            </div>
            <span class="text-sm font-bold text-amber-400 font-mono">{metrics.cashback.pending}</span>
          </div>

          <div class="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div class="flex items-center gap-3">
              <StatusBadge status="APPROVED" />
              <span class="text-xs text-slate-300">Approved & Coins Credited</span>
            </div>
            <span class="text-sm font-bold text-emerald-400 font-mono">{metrics.cashback.approved}</span>
          </div>

          <div class="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div class="flex items-center gap-3">
              <StatusBadge status="REJECTED" />
              <span class="text-xs text-slate-300">Merchant Rejected</span>
            </div>
            <span class="text-sm font-bold text-rose-400 font-mono">{metrics.cashback.rejected}</span>
          </div>

          <div class="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div class="flex items-center gap-3">
              <StatusBadge status="REVERSED" />
              <span class="text-xs text-slate-300">Returned / Order Cancelled</span>
            </div>
            <span class="text-sm font-bold text-slate-400 font-mono">{metrics.cashback.reversed}</span>
          </div>
        </div>
      </div>

      <!-- Top Performing Merchants -->
      <div class="cbk-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-white">Top Partner Merchants</h3>
          <a href="/admin/merchants" class="text-xs text-indigo-400 hover:text-indigo-300 font-medium">Manage All &rarr;</a>
        </div>
        {#if metrics.merchants.top_performers.length === 0}
          <p class="text-xs text-slate-500 py-6 text-center">No merchant conversions recorded yet.</p>
        {:else}
          <div class="divide-y divide-slate-800">
            {#each metrics.merchants.top_performers as merchant}
              <div class="py-3 flex items-center justify-between">
                <div>
                  <h4 class="text-xs font-semibold text-slate-200">{merchant.name}</h4>
                  <span class="text-[10px] text-slate-400 uppercase tracking-wider">{merchant.category}</span>
                </div>
                <div class="text-right">
                  <div class="text-xs font-mono font-bold text-indigo-400">{merchant.conversions} orders</div>
                  <div class="text-[10px] text-slate-400">{merchant.cbk_reward_rate}% reward</div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>
