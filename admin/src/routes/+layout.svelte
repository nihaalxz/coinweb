<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { authState } from '$lib/auth.svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import TopNav from '$lib/components/TopNav.svelte';
  import ManualAdjustmentModal from '$lib/components/ManualAdjustmentModal.svelte';
  import { CheckCircle2, AlertCircle, Info } from 'lucide-svelte';

  let { children } = $props();
  let showAdjustModal = $state(false);

  const isLoginPage = $derived(page.url.pathname.includes('/admin/login'));

  onMount(async () => {
    await authState.init();
    if (!authState.isAuthenticated && !isLoginPage) {
      goto('/admin/login');
    }
  });

  $effect(() => {
    if (!authState.isLoading && !authState.isAuthenticated && !isLoginPage) {
      goto('/admin/login');
    }
  });
</script>

{#if isLoginPage}
  {@render children()}
{:else if authState.isLoading}
  <div class="h-screen w-screen flex flex-col items-center justify-center bg-[#0b0f19] text-slate-400 gap-3">
    <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    <span class="text-xs font-mono tracking-wider text-slate-500">AUTHENTICATING CONSOLE SESSION...</span>
  </div>
{:else if authState.isAuthenticated}
  <div class="flex h-screen overflow-hidden bg-[#0b0f19]">
    <Sidebar />
    <div class="flex-1 flex flex-col min-w-0 overflow-y-auto">
      <TopNav onOpenAdjustModal={() => (showAdjustModal = true)} />
      <main class="flex-1 p-8">
        {@render children()}
      </main>
    </div>
  </div>

  <ManualAdjustmentModal
    isOpen={showAdjustModal}
    onClose={() => (showAdjustModal = false)}
    onSuccess={() => {
      // reload or dispatch event
    }}
  />
{/if}

<!-- Toast Notification -->
{#if authState.toastMessage}
  <div class="fixed bottom-5 right-5 z-50 flex items-center gap-2 px-4 py-3 rounded-lg shadow-2xl text-xs font-medium border animate-in slide-in-from-bottom-5 {
    authState.toastType === 'success'
      ? 'bg-emerald-950/90 text-emerald-300 border-emerald-800'
      : authState.toastType === 'error'
      ? 'bg-rose-950/90 text-rose-300 border-rose-800'
      : 'bg-slate-900 text-slate-200 border-slate-700'
  }">
    {#if authState.toastType === 'success'}
      <CheckCircle2 size={16} class="text-emerald-400 shrink-0" />
    {:else if authState.toastType === 'error'}
      <AlertCircle size={16} class="text-rose-400 shrink-0" />
    {:else}
      <Info size={16} class="text-indigo-400 shrink-0" />
    {/if}
    <span>{authState.toastMessage}</span>
  </div>
{/if}
