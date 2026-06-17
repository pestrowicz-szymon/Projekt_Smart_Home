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
	<path d="m9 18 6-6-6-6" />
</svg>
