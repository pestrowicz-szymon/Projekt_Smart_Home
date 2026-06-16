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
	<polyline points="6 9 12 15 18 9" />
</svg>
