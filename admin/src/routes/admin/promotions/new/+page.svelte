<script lang="ts">
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { authState } from '$lib/auth.svelte';
  import { ArrowLeft, Sparkles, Save } from 'lucide-svelte';

  let title = $state('');
  let slug = $state('');
  let description = $state('');
  let bonusCoins = $state(100);
  let multiplier = $state(1.5);
  let startDate = $state(new Date().toISOString().split('T')[0]);
  let endDate = $state(new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0]);
  let isActive = $state(true);

  let isSubmitting = $state(false);
  let errorMsg = $state('');

  function autoSlug() {
    slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    errorMsg = '';
    isSubmitting = true;

    try {
      await api.post('/admin/promotions/', {
        title: title.trim(),
        slug: slug.trim(),
        description: description.trim(),
        bonus_coins: bonusCoins,
        cashback_multiplier: multiplier,
        start_date: new Date(startDate).toISOString(),
        end_date: new Date(endDate).toISOString(),
        is_active: isActive,
      });
      authState.showToast(`Promotion "${title}" launched successfully.`, 'success');
      goto('/admin/promotions');
    } catch (err: any) {
      errorMsg = err.message || 'Failed to create promotion.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="space-y-6 max-w-2xl">
  <div>
    <a href="/admin/promotions" class="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white mb-3">
      <ArrowLeft size={14} />
      <span>Back to Promotions</span>
    </a>
    <h1 class="text-xl font-bold text-white flex items-center gap-2">
      <Sparkles size={22} class="text-indigo-400" />
      <span>Create Promotional Campaign</span>
    </h1>
    <p class="text-xs text-slate-400 mt-1">Configure time-limited boost events and consumer incentive multipliers</p>
  </div>

  {#if errorMsg}
    <div class="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-xs text-rose-300">{errorMsg}</div>
  {/if}

  <form onsubmit={handleSubmit} class="cbk-card p-6 space-y-4">
    <div>
      <label for="newPromoTitle" class="block text-xs font-semibold text-slate-300 mb-1">Campaign Headline</label>
      <input
        id="newPromoTitle"
        type="text"
        bind:value={title}
        oninput={autoSlug}
        required
        placeholder="e.g. Diwali Super Saver Fest"
        class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
      />
    </div>

    <div>
      <label for="newPromoSlug" class="block text-xs font-semibold text-slate-300 mb-1">Slug</label>
      <input
        id="newPromoSlug"
        type="text"
        bind:value={slug}
        required
        class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
      />
    </div>

    <div>
      <label for="newPromoDesc" class="block text-xs font-semibold text-slate-300 mb-1">Description</label>
      <textarea
        id="newPromoDesc"
        bind:value={description}
        rows={2}
        placeholder="Explain campaign rules to consumers..."
        class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
      ></textarea>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div>
        <label for="newPromoCoins" class="block text-xs font-semibold text-slate-300 mb-1">Bonus Coins Grant</label>
        <input
          id="newPromoCoins"
          type="number"
          min="0"
          bind:value={bonusCoins}
          required
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
        />
      </div>

      <div>
        <label for="newPromoMultiplier" class="block text-xs font-semibold text-slate-300 mb-1">Cashback Multiplier</label>
        <input
          id="newPromoMultiplier"
          type="number"
          step="0.1"
          min="1"
          bind:value={multiplier}
          required
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
        />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div>
        <label for="newPromoStartDate" class="block text-xs font-semibold text-slate-300 mb-1">Start Date</label>
        <input
          id="newPromoStartDate"
          type="date"
          bind:value={startDate}
          required
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
        />
      </div>
      <div>
        <label for="newPromoEndDate" class="block text-xs font-semibold text-slate-300 mb-1">End Date</label>
        <input
          id="newPromoEndDate"
          type="date"
          bind:value={endDate}
          required
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
        />
      </div>
    </div>

    <div class="pt-2">
      <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
        <input type="checkbox" bind:checked={isActive} class="rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0" />
        <span>Active & Enforceable</span>
      </label>
    </div>

    <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
      <a href="/admin/promotions" class="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white">Cancel</a>
      <button
        type="submit"
        disabled={isSubmitting}
        class="flex items-center gap-2 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 disabled:opacity-50"
      >
        <Save size={14} />
        <span>{isSubmitting ? 'Launching...' : 'Launch Campaign'}</span>
      </button>
    </div>
  </form>
</div>
