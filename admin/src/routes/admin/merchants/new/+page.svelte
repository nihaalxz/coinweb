<script lang="ts">
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { authState } from '$lib/auth.svelte';
  import { ArrowLeft, Store, Save } from 'lucide-svelte';

  let name = $state('');
  let slug = $state('');
  let category = $state('marketplaces');
  let websiteUrl = $state('');
  let affiliateNetwork = $state('');
  let affiliateUrlTemplate = $state('');
  let commissionRate = $state(10.0);
  let cbkRewardRate = $state(8.0);
  let rewardBadge = $state('');
  let isFeatured = $state(false);
  let isActive = $state(true);

  let isSubmitting = $state(false);
  let errorMsg = $state('');

  function autoSlug() {
    slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    errorMsg = '';
    isSubmitting = true;

    try {
      await api.post('/admin/merchants/', {
        name: name.trim(),
        slug: slug.trim(),
        category,
        website_url: websiteUrl.trim(),
        affiliate_network: affiliateNetwork.trim(),
        affiliate_url_template: affiliateUrlTemplate.trim(),
        commission_rate: commissionRate,
        cbk_reward_rate: cbkRewardRate,
        reward_badge: rewardBadge.trim(),
        is_featured: isFeatured,
        is_active: isActive,
      });

      authState.showToast(`Merchant "${name}" created successfully.`, 'success');
      goto('/admin/merchants');
    } catch (err: any) {
      errorMsg = err.message || 'Failed to create merchant.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="space-y-6 max-w-3xl">
  <div>
    <a href="/admin/merchants" class="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white mb-3">
      <ArrowLeft size={14} />
      <span>Back to Merchants</span>
    </a>
    <h1 class="text-xl font-bold text-white flex items-center gap-2">
      <Store size={22} class="text-indigo-400" />
      <span>Add Partner Merchant</span>
    </h1>
    <p class="text-xs text-slate-400 mt-1">Configure affiliate tracking and cash reward parameters for an e-commerce partner</p>
  </div>

  {#if errorMsg}
    <div class="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-xs text-rose-300">{errorMsg}</div>
  {/if}

  <form onsubmit={handleSubmit} class="cbk-card p-6 space-y-4">
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label for="newMerchantName" class="block text-xs font-semibold text-slate-300 mb-1">Merchant / Store Name</label>
        <input
          id="newMerchantName"
          type="text"
          bind:value={name}
          oninput={autoSlug}
          required
          placeholder="e.g. Flipkart"
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
        />
      </div>
      <div>
        <label for="newMerchantSlug" class="block text-xs font-semibold text-slate-300 mb-1">Slug Identifier</label>
        <input
          id="newMerchantSlug"
          type="text"
          bind:value={slug}
          required
          placeholder="e.g. flipkart"
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
        />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div>
        <label for="newMerchantCategory" class="block text-xs font-semibold text-slate-300 mb-1">Industry Category</label>
        <select
          id="newMerchantCategory"
          bind:value={category}
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
        >
          <option value="marketplaces">Marketplaces</option>
          <option value="fashion">Fashion</option>
          <option value="electronics">Electronics</option>
          <option value="travel">Travel</option>
          <option value="beauty">Beauty</option>
          <option value="grocery">Grocery</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <label for="newMerchantWebsite" class="block text-xs font-semibold text-slate-300 mb-1">Official Website URL</label>
        <input
          id="newMerchantWebsite"
          type="url"
          bind:value={websiteUrl}
          required
          placeholder="https://www.flipkart.com"
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
        />
      </div>
    </div>

    <div>
      <label for="newMerchantTemplate" class="block text-xs font-semibold text-slate-300 mb-1">Affiliate URL Template</label>
      <input
        id="newMerchantTemplate"
        type="text"
        bind:value={affiliateUrlTemplate}
        placeholder="https://tracking.network.com/aff_c?offer_id=12&aff_id=99&aff_sub=[click_id]&url=https://flipkart.com"
        class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
      />
      <span class="block text-[11px] text-slate-500 mt-1">Available placeholders: {'{click_id}'}, {'{user_id}'}, {'{merchant_slug}'}</span>
    </div>

    <div class="grid grid-cols-3 gap-4">
      <div>
        <label for="newMerchantCommRate" class="block text-xs font-semibold text-slate-300 mb-1">CBK Commission (%)</label>
        <input
          id="newMerchantCommRate"
          type="number"
          step="0.1"
          bind:value={commissionRate}
          required
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
        />
      </div>
      <div>
        <label for="newMerchantRewardRate" class="block text-xs font-semibold text-slate-300 mb-1">Customer Reward (%)</label>
        <input
          id="newMerchantRewardRate"
          type="number"
          step="0.1"
          bind:value={cbkRewardRate}
          required
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
        />
      </div>
      <div>
        <label for="newMerchantBadge" class="block text-xs font-semibold text-slate-300 mb-1">Marketing Badge</label>
        <input
          id="newMerchantBadge"
          type="text"
          bind:value={rewardBadge}
          placeholder="POPULAR, TRENDING"
          class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
        />
      </div>
    </div>

    <div class="flex items-center gap-6 pt-2">
      <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
        <input type="checkbox" bind:checked={isActive} class="rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0" />
        <span>Active on Storefront</span>
      </label>
      <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
        <input type="checkbox" bind:checked={isFeatured} class="rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0" />
        <span>Featured in Hero</span>
      </label>
    </div>

    <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
      <a href="/admin/merchants" class="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white">Cancel</a>
      <button
        type="submit"
        disabled={isSubmitting}
        class="flex items-center gap-2 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 disabled:opacity-50"
      >
        <Save size={14} />
        <span>{isSubmitting ? 'Saving...' : 'Save Merchant'}</span>
      </button>
    </div>
  </form>
</div>
