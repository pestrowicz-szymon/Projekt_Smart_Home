<script>
	import { resolve } from '$app/paths';
	import FormField from '$lib/components/FormField.svelte';

	let { form } = $props();
</script>

<svelte:head>
	<title>Login</title>
</svelte:head>

<form method="POST" class="flex flex-col">
	<p class="mb-4">Use your Smart Home account to continue.</p>

	<FormField name="username" type="text" autocomplete="email" required label="Username" />

	<FormField
		name="password"
		type="password"
		autocomplete="current-password"
		required
		label="Password"
	/>

	{#if form?.error}
		<p class="error">{form.error}</p>
	{/if}

	<button type="submit" class="mb-2 bg-accent py-2 hover:bg-accent-hover">Login</button>
	<a class="sign-up" href={resolve('/register')}>Don't have an account? Sign up</a>
</form>

<style>
</style>
