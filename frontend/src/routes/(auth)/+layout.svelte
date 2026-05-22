<script>
	let { children } = $props();
</script>

<div class="grid min-h-screen place-items-center p-6">
	<div class="w-full max-w-sm rounded-2xl p-8 text-white shadow-2xl backdrop-blur">
		<h1 class="mb-2 text-2xl">Smart Home Systems</h1>

		{@render children()}
	</div>
</div>
