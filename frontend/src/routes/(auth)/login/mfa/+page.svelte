<script>
	import { resolve } from '$app/paths';
	import FormField from '$lib/components/FormField.svelte';

	let { form } = $props();
</script>

<svelte:head>
	<title>MFA Verification</title>
</svelte:head>

<form method="POST" class="flex flex-col">
	<p class="mb-4">
		Multi-Factor Authentication is enabled for your account. Please enter the 6-digit code from your
		authenticator app.
	</p>

	<FormField
		name="mfa_code"
		type="text"
		inputmode="numeric"
		pattern="[0-9][0-9][0-9][0-9][0-9][0-9]"
		autocomplete="one-time-code"
		required
		label="MFA Code"
		placeholder="123456"
	/>

	{#if form?.error}
		<p class="error">{form.error}</p>
	{/if}

	<button type="submit" class="mb-2 bg-accent py-2 hover:bg-accent-hover">Verify & Login</button>
	<a class="sign-up" href={resolve('/login')}>Back to Login</a>
</form>

<style>
</style>
