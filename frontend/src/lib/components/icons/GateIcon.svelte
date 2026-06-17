<script lang="ts">
	import type { SVGAttributes } from 'svelte/elements';
	let props: SVGAttributes<SVGSVGElement> = $props();
</script>

<svg
	viewBox="0 0 24 24"
	fill="none"
	stroke="currentColor"
	stroke-width="2"
	stroke-linecap="round"
	stroke-linejoin="round"
	aria-hidden="true"
	{...props}
>
	<path d="M4 11V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v5" />
	<path d="M10 20v-4" />
	<path d="M14 20v-4" />
	<path d="M18 20v-4" />
	<path d="M2 20h20" />
	<path d="M6 20v-4" />
</svg>
