<script lang="ts">
  import { Settings, Shield, Database, Coins, ArrowDownToLine } from 'lucide-svelte';
</script>

<div class="space-y-6 max-w-4xl">
  <div>
    <h1 class="text-xl font-bold text-white">System Architecture & Financial Configuration</h1>
    <p class="text-xs text-slate-400 mt-1">Review operational constants, database abstraction settings, and role permissions</p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- Financial Peg Configuration -->
    <div class="cbk-card p-6 space-y-4">
      <div class="flex items-center gap-2 text-white font-bold text-sm border-b border-slate-800 pb-3">
        <Coins size={18} class="text-amber-400" />
        <span>Monetary Conversion Standard</span>
      </div>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between py-1 border-b border-slate-800/60">
          <span class="text-slate-400">Fixed Conversion Ratio:</span>
          <strong class="text-amber-400 font-mono">10 CBK Coins = ₹1.00 INR</strong>
        </div>
        <div class="flex justify-between py-1 border-b border-slate-800/60">
          <span class="text-slate-400">Enforcement Layer:</span>
          <span class="font-mono text-indigo-400">wallets.services.CoinService</span>
        </div>
        <div class="flex justify-between py-1 border-b border-slate-800/60">
          <span class="text-slate-400">Floating-Point Policy:</span>
          <span class="text-emerald-400 font-semibold">Strict Decimal (0.01 INR)</span>
        </div>
        <div class="flex justify-between py-1">
          <span class="text-slate-400">Minimum Redemption:</span>
          <span class="font-mono font-bold text-white">500 Coins (₹50.00)</span>
        </div>
      </div>
    </div>

    <!-- Database Abstraction -->
    <div class="cbk-card p-6 space-y-4">
      <div class="flex items-center gap-2 text-white font-bold text-sm border-b border-slate-800 pb-3">
        <Database size={18} class="text-indigo-400" />
        <span>Database Abstraction Layer</span>
      </div>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between py-1 border-b border-slate-800/60">
          <span class="text-slate-400">Active Engine:</span>
          <span class="font-mono text-emerald-400 font-bold">SQLite / MySQL Dynamic ORM</span>
        </div>
        <div class="flex justify-between py-1 border-b border-slate-800/60">
          <span class="text-slate-400">Environment Switcher:</span>
          <span class="font-mono text-slate-300">DATABASE_ENGINE (.env)</span>
        </div>
        <div class="flex justify-between py-1 border-b border-slate-800/60">
          <span class="text-slate-400">MySQL Driver:</span>
          <span class="font-mono text-indigo-300">PyMySQL (Cross-platform)</span>
        </div>
        <div class="flex justify-between py-1">
          <span class="text-slate-400">Ledger Locking:</span>
          <span class="font-mono text-emerald-400 font-bold">select_for_update() (Atomic)</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Role-Based Permissions Matrix -->
  <div class="cbk-card p-6">
    <div class="flex items-center gap-2 text-white font-bold text-sm border-b border-slate-800 pb-3 mb-4">
      <Shield size={18} class="text-indigo-400" />
      <span>Role-Based Access Control (RBAC) Matrix</span>
    </div>

    <table class="cbk-table">
      <thead>
        <tr>
          <th>Role</th>
          <th>User Mgmt</th>
          <th>Wallet Ledger</th>
          <th>Manual Adjustments</th>
          <th>Cashback Ops</th>
          <th>Payouts (UPI)</th>
          <th>Merchants</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800/80 text-xs">
        <tr>
          <td class="font-bold text-indigo-300 font-mono">SUPER_ADMIN</td>
          <td class="text-emerald-400">Full</td>
          <td class="text-emerald-400">Full</td>
          <td class="text-emerald-400">Full</td>
          <td class="text-emerald-400">Full</td>
          <td class="text-emerald-400">Full</td>
          <td class="text-emerald-400">Full</td>
        </tr>
        <tr>
          <td class="font-bold text-slate-200 font-mono">FINANCE_ADMIN</td>
          <td class="text-slate-400">Read</td>
          <td class="text-emerald-400">Full</td>
          <td class="text-emerald-400">Authorized</td>
          <td class="text-slate-400">Read</td>
          <td class="text-emerald-400">Full Payouts</td>
          <td class="text-slate-400">Read</td>
        </tr>
        <tr>
          <td class="font-bold text-slate-200 font-mono">OPERATIONS_ADMIN</td>
          <td class="text-emerald-400">Manage</td>
          <td class="text-slate-400">Read</td>
          <td class="text-slate-500">None</td>
          <td class="text-emerald-400">Reconciliation</td>
          <td class="text-slate-400">Read</td>
          <td class="text-emerald-400">Manage</td>
        </tr>
        <tr>
          <td class="font-bold text-slate-200 font-mono">MARKETING_ADMIN</td>
          <td class="text-slate-500">None</td>
          <td class="text-slate-500">None</td>
          <td class="text-slate-500">None</td>
          <td class="text-slate-400">Read</td>
          <td class="text-slate-500">None</td>
          <td class="text-emerald-400">Manage + Promos</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
