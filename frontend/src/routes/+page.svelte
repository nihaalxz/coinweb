<script lang="ts">
	import Toast from '$lib/components/Toast.svelte';
	import Navbar from '$lib/components/Navbar.svelte';
	import Hero from '$lib/components/Hero.svelte';
	import StrategicEcosystem from '$lib/components/StrategicEcosystem.svelte';
	import GoalSection from '$lib/components/GoalSection.svelte';
	import SteppingStones from '$lib/components/SteppingStones.svelte';
	import RewardsSystem from '$lib/components/RewardsSystem.svelte';
	import EverythingYouNeed from '$lib/components/EverythingYouNeed.svelte';
	import StoreDiscovery from '$lib/components/StoreDiscovery.svelte';
	import ProductDealsShowcase from '$lib/components/ProductDealsShowcase.svelte';
	import AppExperience from '$lib/components/AppExperience.svelte';
	import PartnersGrid from '$lib/components/PartnersGrid.svelte';
	import Testimonial from '$lib/components/Testimonial.svelte';
	import SkyCta from '$lib/components/SkyCta.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import LegalModal from '$lib/components/LegalModal.svelte';
</script>

<Toast />
<Navbar />

<main>
	<Hero />
	<StrategicEcosystem />
	<GoalSection />
	<SteppingStones />
	<RewardsSystem />
	<EverythingYouNeed />
	<StoreDiscovery />
	<ProductDealsShowcase />
	<AppExperience />
	<PartnersGrid />
	<Testimonial />
	<SkyCta />
</main>

<Footer />
<LegalModal />
