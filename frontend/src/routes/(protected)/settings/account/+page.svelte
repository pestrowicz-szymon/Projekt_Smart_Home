<script lang="ts">
	import { enhance } from '$app/forms';
	import QRCode from 'qrcode';
	import FormField from '$lib/components/FormField.svelte';
	import { ChevronRightIcon, UserIcon } from '$lib/components/icons';
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
	<title>Account Settings</title>
</svelte:head>

<div class="flex flex-col gap-8">
	<section>
		<h1 class="mb-2 text-2xl font-bold">Account</h1>
		<p class="text-foreground-muted">Manage your security and personal information.</p>
	</section>

	<section class="space-y-4">
		<h2 class="px-2 text-sm font-bold uppercase tracking-wider text-foreground-subtle">Security</h2>

		<div
			class="overflow-hidden rounded-xl border border-line bg-surface-raised divide-y divide-line"
		>
			<!-- MFA Toggle / Status -->
			<div class="p-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<div class="rounded-lg bg-accent-soft p-2 text-accent">
							<UserIcon class="h-5 w-5" />
						</div>
						<div>
							<p class="font-medium text-foreground">Multi-Factor Authentication</p>
							<p class="text-xs text-foreground-muted">
								{mfaEnabled ? 'Enabled' : 'Adds an extra layer of security'}
							</p>
						</div>
					</div>

					{#if mfaEnabled}
						<form method="POST" action="?/disableMfa" use:enhance>
							<button type="submit" class="text-sm font-semibold text-danger hover:underline">
								Disable
							</button>
						</form>
					{:else if !mfaSetup}
						<form method="POST" action="?/setupMfa" use:enhance>
							<button type="submit" class="text-sm font-semibold text-accent hover:underline">
								Set up
							</button>
						</form>
					{/if}
				</div>

				{#if mfaSetup}
					<div class="mt-6 flex flex-col gap-4 border-t border-line pt-6">
						<p class="font-medium text-foreground">Complete MFA Setup</p>
						<p class="text-sm text-foreground-muted">
							Scan this QR code in your authenticator app.
						</p>

						<div class="flex justify-center rounded-lg bg-white p-4 shadow-sm border border-line">
							<canvas bind:this={canvas}></canvas>
						</div>

						<div
							class="rounded-md bg-surface-sunken p-3 font-mono text-sm break-all text-center border border-line"
						>
							{mfaSetup.secret}
						</div>

						<form method="POST" action="?/verifyMfa" use:enhance class="flex flex-col gap-4">
							<FormField
								name="code"
								label="Verification Code"
								placeholder="123456"
								required
								inputmode="numeric"
								pattern="[0-9]{'{'}6}"
							/>
							{#if form?.error && form.action === 'verifyMfa'}
								<p class="text-sm text-danger">{form.error}</p>
							{/if}
							<button
								type="submit"
								class="rounded-md bg-accent px-4 py-2 text-white font-medium hover:bg-accent-hover transition-colors"
							>
								Verify and Enable
							</button>
						</form>
					</div>
				{/if}
			</div>

			<!-- Placeholder for other account actions -->
			<div
				class="flex items-center justify-between p-4 transition-colors hover:bg-surface-sunken cursor-not-allowed opacity-50"
			>
				<div class="flex items-center gap-3">
					<div class="rounded-lg bg-muted-soft p-2 text-muted">
						<UserIcon class="h-5 w-5" />
					</div>
					<div>
						<p class="font-medium text-foreground">Change Password</p>
						<p class="text-xs text-foreground-muted">Coming soon</p>
					</div>
				</div>
				<ChevronRightIcon class="h-5 w-5 text-foreground-subtle" />
			</div>
		</div>
	</section>
</div>
