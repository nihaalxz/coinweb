<script lang="ts">
  import { goto } from '$app/navigation';
  import { authState } from '$lib/auth.svelte';
  import { Lock, Mail, Shield, AlertCircle } from 'lucide-svelte';

  let email = $state('admin@cashbackkart.in');
  let password = $state('Admin@123CBKSecure');
  let errorMsg = $state('');
  let isSubmitting = $state(false);

  async function handleLogin(e: SubmitEvent) {
    e.preventDefault();
    errorMsg = '';
    isSubmitting = true;

    try {
      await authState.login(email.trim(), password);
      goto('/admin');
    } catch (err: any) {
      errorMsg = err.message || 'Invalid administrator credentials.';
    } finally {
      isSubmitting = false;
    }
  }

  function fillDemoCreds(roleEmail: string) {
    email = roleEmail;
    password = 'Admin@123CBKSecure';
  }
</script>

<div class="min-h-screen w-screen flex items-center justify-center bg-[#070a11] px-4 py-12 select-none relative overflow-hidden">
  <!-- Subtle ambient glow -->
  <div class="absolute -top-40 -left-40 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>
  <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>

  <div class="w-full max-w-md">
    <!-- Brand Box -->
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-600 text-white font-black text-lg tracking-wider shadow-xl shadow-indigo-600/30 mb-3">
        CBK
      </div>
      <h1 class="text-xl font-bold text-white tracking-tight">Cash Back Kart</h1>
      <p class="text-xs text-indigo-400 font-semibold tracking-wider uppercase mt-0.5">Fintech Operations Console</p>
    </div>

    <!-- Login Card -->
    <div class="cbk-card p-8 shadow-2xl border-slate-800 bg-[#0f172a]/95 backdrop-blur-xl">
      <div class="flex items-center justify-between pb-4 mb-5 border-b border-slate-800">
        <div>
          <h2 class="text-sm font-bold text-white">Administrator Sign In</h2>
          <p class="text-[11px] text-slate-400">Strictly authorized staff and ops personnel only</p>
        </div>
        <Shield size={20} class="text-indigo-400" />
      </div>

      {#if errorMsg}
        <div class="p-3 mb-5 rounded-lg bg-rose-950/70 border border-rose-800 text-xs text-rose-300 flex items-start gap-2">
          <AlertCircle size={16} class="text-rose-400 shrink-0 mt-0.5" />
          <span>{errorMsg}</span>
        </div>
      {/if}

      <form onsubmit={handleLogin} class="space-y-4">
        <div>
          <label for="adminEmailInput" class="block text-xs font-semibold text-slate-300 mb-1">Work Email</label>
          <div class="relative">
            <Mail size={16} class="absolute left-3 top-2.5 text-slate-500" />
            <input
              id="adminEmailInput"
              type="email"
              bind:value={email}
              required
              placeholder="admin@cashbackkart.in"
              class="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>
        </div>

        <div>
          <label for="adminPasswordInput" class="block text-xs font-semibold text-slate-300 mb-1">Access Password</label>
          <div class="relative">
            <Lock size={16} class="absolute left-3 top-2.5 text-slate-500" />
            <input
              id="adminPasswordInput"
              type="password"
              bind:value={password}
              required
              placeholder="••••••••••••"
              class="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          class="w-full mt-2 py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold tracking-wide shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
        >
          {isSubmitting ? 'Authenticating...' : 'Enter Console'}
        </button>
      </form>

      <!-- Quick Fill Demo Roles -->
      <div class="mt-6 pt-5 border-t border-slate-800 text-[11px] text-slate-400">
        <span class="block mb-2 font-medium text-slate-500">Quick Test Credentials:</span>
        <div class="flex flex-wrap gap-1.5">
          <button
            type="button"
            onclick={() => fillDemoCreds('admin@cashbackkart.in')}
            class="px-2 py-1 rounded bg-slate-800/80 hover:bg-slate-700 text-[10px] text-slate-300 font-mono transition-colors"
          >
            Super Admin
          </button>
          <button
            type="button"
            onclick={() => fillDemoCreds('finance@cashbackkart.in')}
            class="px-2 py-1 rounded bg-slate-800/80 hover:bg-slate-700 text-[10px] text-slate-300 font-mono transition-colors"
          >
            Finance Admin
          </button>
          <button
            type="button"
            onclick={() => fillDemoCreds('ops@cashbackkart.in')}
            class="px-2 py-1 rounded bg-slate-800/80 hover:bg-slate-700 text-[10px] text-slate-300 font-mono transition-colors"
          >
            Ops Admin
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
