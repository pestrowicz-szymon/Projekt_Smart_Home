<script lang="ts">
	import { enhance } from '$app/forms';
	import QRCode from 'qrcode';
	import FormField from '$lib/components/FormField.svelte';
	import type { HomeMembership } from '$lib/types/auth';
	import type { ActionData, PageData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let mfaEnabled = $derived(
		data.mfaStatus?.enabled || (form?.success && form.action === 'verifyMfa')
	);
	let mfaSetup = $derived(form?.mfaSetup);

	let canvas: HTMLCanvasElement | undefined = $state();

	$effect(() => {
		if (mfaSetup?.otpauth_uri && canvas) {
			QRCode.toCanvas(canvas, mfaSetup.otpauth_uri, {
				width: 200,
				margin: 2,
				color: {
					dark: '#000000',
					light: '#ffffff'
				}
			}).catch((err) => {
				console.error('Failed to generate QR code:', err);
			});
		}
	});
</script>

<svelte:head>
	<title>Preferences</title>
</svelte:head>

<div class="flex flex-col gap-8 p-4">
	<section>
		<h1 class="mb-2 text-2xl font-bold">Preferences</h1>
		<p class="text-foreground-muted">Manage your account and home settings.</p>
	</section>

	<section class="rounded-lg border border-border p-4">
		<h2 class="mb-4 text-xl font-semibold">Multi-Factor Authentication (MFA)</h2>

		{#if mfaEnabled}
			<div class="flex flex-col gap-4">
				<p class="text-green-500">MFA is currently enabled for your account.</p>
				<form method="POST" action="?/disableMfa" use:enhance>
					<button type="submit" class="rounded bg-red-600 px-4 py-2 text-white hover:bg-red-700">
						Disable MFA
					</button>
				</form>
			</div>
		{:else if mfaSetup}
			<div class="flex flex-col gap-4">
				<p class="font-medium">Setup MFA</p>
				<p class="text-sm text-foreground-muted">
					Scan this QR code or enter the secret in your authenticator app (e.g., Google
					Authenticator, Authy).
				</p>

				<div class="flex justify-center rounded bg-white p-4 shadow-sm">
					<canvas bind:this={canvas}></canvas>
				</div>

				<div class="rounded bg-muted p-3 font-mono text-lg break-all">
					{mfaSetup.secret}
				</div>
				<p class="text-sm">
					Or use this link: <a href={mfaSetup.otpauth_uri} class="text-accent underline"
						>Add to App</a
					>
				</p>

				<form method="POST" action="?/verifyMfa" use:enhance class="flex flex-col gap-4">
					<FormField
						name="code"
						label="Verification Code"
						placeholder="123456"
						required
						inputmode="numeric"
						pattern="[0-9][0-9][0-9][0-9][0-9][0-9]"
					/>
					{#if form?.error && form.action === 'verifyMfa'}
						<p class="text-sm text-red-500">{form.error}</p>
					{/if}
					<button
						type="submit"
						class="rounded bg-accent px-4 py-2 text-white hover:bg-accent-hover"
					>
						Verify and Enable
					</button>
				</form>
			</div>
		{:else}
			<div class="flex flex-col gap-4">
				<p class="text-foreground-muted">MFA adds an extra layer of security to your account.</p>
				<form method="POST" action="?/setupMfa" use:enhance>
					<button
						type="submit"
						class="rounded bg-accent px-4 py-2 text-white hover:bg-accent-hover"
					>
						Enable MFA
					</button>
				</form>
			</div>
		{/if}
	</section>

	{#if data.manageableHomes.length > 0}
		<section class="rounded-lg border border-border p-4">
			<h2 class="mb-4 text-xl font-semibold">Home Management</h2>
			<div class="flex flex-col gap-4">
				{#each data.manageableHomes as home (home.id)}
					{@const membership = data.user?.home_memberships.find(
						(m: HomeMembership) => m.home.id === home.id
					)}
					{#if membership}
						<div
							class="flex items-center justify-between border-b border-border pb-2 last:border-0"
						>
							<div>
								<p class="font-medium">{home.name}</p>
								<p class="text-sm text-foreground-muted">Role: {membership.role}</p>
							</div>
							<form method="POST" action="?/toggleDeviceManagement" use:enhance>
								<input type="hidden" name="membership_id" value={membership.id} />
								<label class="flex cursor-pointer items-center gap-2">
									<input
										type="checkbox"
										name="can_manage_devices"
										checked={membership.can_manage_devices}
										onchange={(e) => e.currentTarget.form?.requestSubmit()}
										class="h-4 w-4 rounded border-gray-300 text-accent focus:ring-accent"
									/>
									<span class="text-sm">Manage Devices</span>
								</label>
							</form>
						</div>
					{/if}
				{/each}
			</div>
		</section>
	{/if}
</div>
