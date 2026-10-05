<script lang="ts">
  import { API_BASE, getAuthToken } from '$lib/api';
  import { Download, FileText, BarChart3, ShieldCheck } from 'lucide-svelte';

  const reportItems = [
    {
      title: 'Registered Users Directory Report',
      desc: 'Complete export of all user accounts, roles, verification states, phone numbers, and balances.',
      endpoint: '/admin/reports/users/csv/',
      filename: 'cbk_users_report.csv',
      category: 'Users & Accounts'
    },
    {
      title: 'Immutable Coin Ledger Transactions',
      desc: 'Comprehensive financial audit trail including all credits, debits, reversals, INR values, and balance deltas.',
      endpoint: '/admin/reports/transactions/csv/',
      filename: 'cbk_transactions_ledger.csv',
      category: 'Financial Ledger'
    },
    {
      title: 'Cashback Claims & Conversions Report',
      desc: 'Order numbers, affiliate commission margins, cashback in INR and coins, and reconciliation approval dates.',
      endpoint: '/admin/reports/cashback/csv/',
      filename: 'cbk_cashback_report.csv',
      category: 'Commerce & Orders'
    },
    {
      title: 'Redemption & UPI Payouts Report',
      desc: 'Payout request logs with masked identifiers, coins redeemed, settlement amounts, and bank UTR numbers.',
      endpoint: '/admin/reports/redemptions/csv/',
      filename: 'cbk_redemptions_report.csv',
      category: 'Financial Payouts'
    },
  ];

  function downloadCsv(endpoint: string, filename: string) {
    const token = getAuthToken();
    const url = `${API_BASE}${endpoint}`;

    fetch(url, {
      headers: {
        Authorization: token ? `Token ${token}` : '',
      },
    })
      .then((res) => res.blob())
      .then((blob) => {
        const a = document.createElement('a');
        a.href = window.URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
      })
      .catch((err) => {
        alert('Failed to download report: ' + err.message);
      });
  }
</script>

<div class="space-y-6 max-w-5xl">
  <div>
    <h1 class="text-xl font-bold text-white">Financial & Operational Reports</h1>
    <p class="text-xs text-slate-400 mt-1">Export raw transactional datasets and audit summaries in CSV format directly from the database</p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
    {#each reportItems as item}
      <div class="cbk-card p-6 flex flex-col justify-between space-y-4 hover:border-slate-700 transition-colors">
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] uppercase font-bold tracking-wider text-indigo-400 font-mono">{item.category}</span>
            <FileText size={16} class="text-slate-500" />
          </div>
          <h2 class="text-sm font-bold text-white mb-1.5">{item.title}</h2>
          <p class="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
        </div>

        <div class="pt-2">
          <button
            onclick={() => downloadCsv(item.endpoint, item.filename)}
            class="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-white shadow-sm transition-all"
          >
            <Download size={14} class="text-indigo-400" />
            <span>Download CSV Export</span>
          </button>
        </div>
      </div>
    {/each}
  </div>

  <div class="cbk-card p-5 bg-slate-900/60 border-slate-800 text-xs text-slate-400 space-y-2">
    <div class="flex items-center gap-2 text-slate-200 font-semibold">
      <ShieldCheck size={16} class="text-emerald-400" />
      <span>Strict Data Audit Standards</span>
    </div>
    <p class="leading-relaxed text-[11px]">
      All exported reports are compiled live from production database tables without synthetic interpolation. Financial amounts are converted using the fixed standard rule: <strong>10 CBK Coins = ₹1 INR</strong>.
    </p>
  </div>
</div>
