<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { fly, fade } from 'svelte/transition';
	import type { User } from '$lib/types/auth';
	import {
		HomeIcon,
		ChevronDownIcon,
		DoorIcon,
		ClockIcon,
		UsersIcon,
		SettingsIcon,
		UserIcon,
		SlidersIcon,
		LogoutIcon
	} from '$lib/components/icons';

	interface Props {
		open: boolean;
		user?: User;
		activeHomeName?: string;
	}

	let { open = $bindable(), user, activeHomeName }: Props = $props();

	const homeId = $derived(page.params.homeId);

	function close() {
		open = false;
	}

	function onKey(e: KeyboardEvent) {
		if (e.key === 'Escape') close();
	}

	const displayName = $derived(user?.first_name || user?.username || 'Account');
</script>

<svelte:window onkeydown={onKey} />

{#if open}
	<div
		class="fixed inset-0 z-50 bg-overlay"
		role="presentation"
		onclick={close}
		transition:fade={{ duration: 150 }}
	></div>

	<div
		class="fixed inset-x-0 bottom-0 z-50 max-h-[85dvh] overflow-y-auto rounded-t-xl border-t border-line bg-surface pb-[env(safe-area-inset-bottom)] shadow-2xl"
		role="dialog"
		aria-modal="true"
		aria-label="More options"
		transition:fly={{ y: 400, duration: 220 }}
	>
		<div class="flex justify-center pt-2 pb-1">
			<span class="h-1.5 w-10 rounded-pill bg-line-strong"></span>
		</div>

		<a
			href={resolve('/h')}
			onclick={close}
			class="mx-3 my-2 flex items-center justify-between rounded-md bg-surface-raised px-4 py-3 transition-colors hover:bg-surface-sunken"
		>
			<span class="flex items-center gap-3">
				<HomeIcon class="h-5 w-5 text-accent" />
				<span class="font-medium text-foreground">{activeHomeName ?? 'Select home'}</span>
			</span>
			<ChevronDownIcon class="h-4 w-4 text-foreground-muted" />
		</a>

		<ul class="mx-3 my-2 divide-y divide-line overflow-hidden rounded-md bg-surface-raised">
			<li>
				<a
					href={homeId ? resolve(`/h/${homeId}/rooms`) : resolve('/h')}
					onclick={close}
					class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-sunken"
				>
					<DoorIcon class="h-5 w-5 text-foreground-muted" />
					<span class="text-foreground">Rooms</span>
				</a>
			</li>
			<li>
				<a
					href={homeId ? resolve(`/h/${homeId}/activity`) : resolve('/h')}
					onclick={close}
					class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-sunken"
				>
					<ClockIcon class="h-5 w-5 text-foreground-muted" />
					<span class="text-foreground">Activity</span>
				</a>
			</li>
			<li>
				<a
					href={homeId ? resolve(`/h/${homeId}/members`) : resolve('/h')}
					onclick={close}
					class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-sunken"
				>
					<UsersIcon class="h-5 w-5 text-foreground-muted" />
					<span class="text-foreground">Members</span>
				</a>
			</li>
			<li>
				<a
					href={homeId ? resolve(`/h/${homeId}/settings`) : resolve('/h')}
					onclick={close}
					class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-sunken"
				>
					<SettingsIcon class="h-5 w-5 text-foreground-muted" />
					<span class="text-foreground">Home settings</span>
				</a>
			</li>
		</ul>

		<ul class="mx-3 my-2 divide-y divide-line overflow-hidden rounded-md bg-surface-raised">
			<li>
				<a
					href={resolve('/settings/account')}
					onclick={close}
					class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-sunken"
				>
					<UserIcon class="h-5 w-5 text-foreground-muted" />
					<span class="text-foreground">{displayName}</span>
				</a>
			</li>
			<li>
				<a
					href={resolve('/settings/preferences')}
					onclick={close}
					class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-sunken"
				>
					<SlidersIcon class="h-5 w-5 text-foreground-muted" />
					<span class="text-foreground">Preferences</span>
				</a>
			</li>
			<li>
				<form method="POST" action={resolve('/logout')} class="contents">
					<button
						type="submit"
						class="flex w-full items-center gap-3 px-4 py-3 text-left text-danger transition-colors hover:bg-surface-sunken"
					>
						<LogoutIcon class="h-5 w-5" />
						<span>Sign out</span>
					</button>
				</form>
			</li>
		</ul>
	</div>
{/if}
