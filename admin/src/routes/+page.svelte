<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  onMount(() => {
    goto('/admin');
  });
</script>

<div class="p-8 text-center text-slate-500 text-xs">Redirecting to console...</div>
