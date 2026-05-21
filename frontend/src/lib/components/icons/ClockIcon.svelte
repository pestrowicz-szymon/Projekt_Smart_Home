<script lang="ts">
	import type { SVGAttributes } from 'svelte/elements';
	let { ...rest }: SVGAttributes<SVGSVGElement> = $props();
</script>

<svg
	viewBox="0 0 24 24"
	fill="none"
	stroke="currentColor"
	stroke-width="2"
	stroke-linecap="round"
	stroke-linejoin="round"
	aria-hidden="true"
	{...rest}
>
	<circle cx="12" cy="12" r="10" />
	<polyline points="12 6 12 12 16 14" />
</svg>
