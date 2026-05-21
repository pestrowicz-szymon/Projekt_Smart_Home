<script lang="ts">
	import FormField from '$lib/components/FormField.svelte';
	import { resolve } from '$app/paths';
	import type { ActionData } from './$types';
	let { form }: { form: ActionData } = $props();
</script>

<svelte:head>
	<title>Register</title>
</svelte:head>

<form method="POST" class="flex flex-col">
	<p>Register for a new account.</p>

	{#if form?.formError}
		<p class="message">{form.formError}</p>
	{/if}

	<FormField
		name="first_name"
		type="text"
		autocomplete="given-name"
		required
		label="First Name"
		value={form?.values?.first_name}
		error={form?.fieldErrors?.first_name}
	/>

	<FormField
		name="last_name"
		type="text"
		autocomplete="family-name"
		required
		label="Last Name"
		value={form?.values?.last_name}
		error={form?.fieldErrors?.last_name}
	/>

	<FormField
		name="username"
		type="text"
		autocomplete="username"
		required
		label="Username"
		value={form?.values?.username}
		error={form?.fieldErrors?.username}
	/>

	<FormField
		name="email"
		type="email"
		autocomplete="email"
		required
		label="Email"
		value={form?.values?.email}
		error={form?.fieldErrors?.email}
	/>
	<FormField
		name="password"
		type="password"
		autocomplete="new-password"
		required
		label="Password"
		error={form?.fieldErrors?.password}
	/>

	<FormField
		name="password2"
		type="password"
		autocomplete="new-password"
		required
		label="Confirm Password"
		error={form?.fieldErrors?.confirm_password}
	/>

	<button type="submit" class="mb-2 bg-accent py-2 hover:bg-accent-hover">Register</button>
	<a class="sign-up" href={resolve('/login')}>Already have an account? Login</a>
</form>

<style>
</style>
