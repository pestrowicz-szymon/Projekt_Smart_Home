<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { copyToClipboard } from '$lib/utils/copy';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const invites = $derived(data.invites);
	let copiedCode: string | null = $state(null);

	$effect(() => {
		if (form?.success || form?.revoked) {
			invalidateAll();
		}
	});

	async function handleCopy(code: string) {
		const success = await copyToClipboard(code);
		if (success) {
			copiedCode = code;
			setTimeout(() => {
				copiedCode = null;
			}, 2000);
		}
	}

	function getInviteLink(code: string): string {
		if (typeof window === 'undefined') return '';
		return `${window.location.origin}/h/join?code=${code}`;
	}

	function getStatusBadgeClass(status: string): string {
		switch (status) {
			case 'active':
				return 'bg-success-soft text-success';
			case 'used':
				return 'bg-surface-sunken text-foreground-muted';
			case 'expired':
				return 'bg-warning-soft text-warning';
			case 'revoked':
				return 'bg-danger-soft text-danger';
			default:
				return 'bg-surface-sunken text-foreground-muted';
		}
	}

	function isExpired(expiresAt: string): boolean {
		return new Date(expiresAt) < new Date();
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head><title>Invitations</title></svelte:head>

<div class="flex flex-col gap-6">
	<div>
		<h1 class="mb-1 text-2xl">Access Management</h1>
		<p class="text-foreground-muted">Invite people or add them directly to your home.</p>
	</div>

	<!-- Generate invite code section -->
	<section class="rounded-lg border border-line bg-surface-raised p-4">
		<h2 class="mb-4 text-md font-medium text-foreground">Generate invitation link</h2>

		<form method="POST" action="?/create" class="flex flex-col gap-3">
			<label class="flex flex-col gap-1">
				<span class="text-sm">Expires in</span>
				<select name="expires_in_hours" required>
					<option value="1">1 hour</option>
					<option value="24" selected>24 hours</option>
					<option value="72">3 days</option>
					<option value="168">1 week</option>
					<option value="720">30 days</option>
				</select>
			</label>

			{#if form?.error && form?.action !== 'addById'}
				<p class="text-danger">{form.error}</p>
			{/if}

			<button
				type="submit"
				class="self-start rounded-md bg-accent px-4 py-2 text-surface hover:bg-accent-hover"
			>
				Generate invite
			</button>
		</form>
	</section>

	<!-- Add member by ID section -->
	<section class="rounded-lg border border-line bg-surface-raised p-4">
		<h2 class="mb-1 text-md font-medium text-foreground">Add member by ID</h2>
		<p class="mb-4 text-sm text-foreground-muted">
			Ask the person to share their User ID from their profile.
		</p>

		<form method="POST" action="?/addById" class="flex flex-col gap-3">
			<label class="flex flex-col gap-1">
				<span class="text-sm">User ID</span>
				<input name="user_id" type="number" min="1" required placeholder="e.g. 42" />
			</label>

			<label class="flex flex-col gap-1">
				<span class="text-sm">Role</span>
				<select name="role">
					<option value="member" selected>Member — can view and use</option>
					<option value="admin">Admin — can manage members and devices</option>
					<option value="viewer">Viewer — read-only access</option>
				</select>
			</label>

			<label class="flex items-center gap-2 text-sm">
				<input name="can_manage_devices" type="checkbox" />
				Can manage devices (regardless of role)
			</label>

			{#if form?.error && form?.action === 'addById'}
				<p class="text-danger">{form.error}</p>
			{/if}
			{#if form?.success && form?.action === 'addById'}
				<p class="text-success">Member added successfully.</p>
			{/if}

			<button
				type="submit"
				class="self-start rounded-md bg-accent px-4 py-2 text-surface hover:bg-accent-hover"
			>
				Add member
			</button>
		</form>
	</section>

	<!-- Invites list -->
	{#if invites && invites.length > 0}
		<section>
			<h2 class="mb-3 text-md font-medium text-foreground">Invitation links</h2>
			<ul class="divide-y divide-line overflow-hidden rounded-md border border-line bg-surface-raised">
				{#each invites as invite (invite.id)}
					{@const expired = isExpired(invite.expires_at)}
					{@const status = invite.revoked_at ? 'revoked' : invite.used_at ? 'used' : expired ? 'expired' : 'active'}
					<li class="flex items-center justify-between gap-3 px-4 py-3">
						<div class="min-w-0 flex-1">
							<div class="flex items-center gap-2">
								<code class="break-all rounded bg-surface-sunken px-2 py-1 font-mono text-xs">
									{invite.code ? invite.code.substring(0, 16) + '...' : 'Hidden'}
								</code>
								<span class="rounded-pill px-2 py-0.5 text-xs {getStatusBadgeClass(status)}">
									{status}
								</span>
							</div>
							<p class="mt-1 text-xs text-foreground-muted">
								{#if invite.used_at}
									Used by {invite.used_by?.first_name} {invite.used_by?.last_name} on {formatDate(invite.used_at)}
								{:else if invite.revoked_at}
									Revoked {formatDate(invite.revoked_at)}
								{:else}
									Expires {formatDate(invite.expires_at)}
								{/if}
							</p>
						</div>

						{#if status === 'active'}
							<div class="flex flex-shrink-0 gap-2">
								<button
									type="button"
									onclick={() => handleCopy(invite.code || '')}
									class="rounded-md px-2 py-1 text-xs {copiedCode === invite.code
										? 'bg-success-soft text-success'
										: 'text-accent hover:bg-accent-soft'}"
								>
									{copiedCode === invite.code ? '✓ Copied' : 'Copy'}
								</button>
								<form method="POST" action="?/revoke" onsubmit={(e) => {
									if (!confirm('Revoke this invite? It will no longer work.')) {
										e.preventDefault();
									}
								}}>
									<input type="hidden" name="id" value={invite.id} />
									<button
										type="submit"
										class="rounded-md px-2 py-1 text-xs text-danger hover:bg-danger-soft"
									>
										Revoke
									</button>
								</form>
							</div>
						{/if}
					</li>
				{/each}
			</ul>
		</section>
	{:else}
		<div class="rounded-lg border border-line bg-surface-raised p-6 text-center">
			<p class="text-foreground-muted">No invitation links yet. Generate one to get started.</p>
		</div>
	{/if}
</div>
