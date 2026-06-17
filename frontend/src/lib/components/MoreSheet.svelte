<script lang="ts">
	import { Drawer } from 'vaul-svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import type { User } from '$lib/types/auth';
	import {
		HomeIcon,
		ChevronDownIcon,
		ChevronRightIcon,
		DoorIcon,
		ClockIcon,
		UsersIcon,
		SettingsIcon,
		UserIcon,
		SlidersIcon,
		LogoutIcon,
		GateIcon
	} from '$lib/components/icons';

	interface Props {
		open: boolean;
		user?: User;
		activeHomeName?: string;
	}

	let { open = $bindable(), user, activeHomeName }: Props = $props();

	const homeId = $derived(page.params.homeId);
	const displayName = $derived(user?.first_name || user?.username || 'Account');

	function close() {
		open = false;
	}

	const listContainerClass =
		'mx-3 my-2 divide-y divide-line overflow-hidden rounded-xl bg-surface-raised border border-line';
	const itemLinkClass =
		'flex items-center justify-between px-4 py-3 transition-colors hover:bg-surface-sunken';
	const itemContentClass = 'flex items-center gap-3';
	const sectionTitleClass =
		'mx-5 mt-4 mb-1 text-[11px] font-bold uppercase tracking-wider text-foreground-subtle';
</script>

<Drawer.Root bind:open closeThreshold={0.25}>
	<Drawer.Portal>
		<Drawer.Overlay class="fixed inset-0 z-50 bg-overlay" />
		<Drawer.Content
			class="fixed inset-x-0 bottom-0 z-50 flex max-h-[90dvh] flex-col rounded-t-xl border-t border-line bg-surface pb-[env(safe-area-inset-bottom)] shadow-2xl outline-none"
		>
			<Drawer.Title class="sr-only">More options</Drawer.Title>
			<Drawer.Description class="sr-only">
				Switch homes, navigate to settings, or sign out.
			</Drawer.Description>

			<div class="overflow-y-auto pb-6">
				<!-- Home Switcher -->
				<a
					href={resolve('/h')}
					onclick={close}
					class="mx-3 my-4 flex items-center justify-between rounded-xl bg-accent-soft border border-line-accent px-4 py-4 transition-colors hover:bg-surface-raised"
				>
					<span class="flex items-center gap-3">
						<HomeIcon class="h-6 w-6 text-accent" />
						<span class="font-bold text-foreground">{activeHomeName ?? 'Select home'}</span>
					</span>
					<ChevronDownIcon class="h-5 w-5 text-accent" />
				</a>

				<!-- Current Home Section -->
				{#if homeId}
					<h3 class={sectionTitleClass}>Current Home</h3>
					<ul class={listContainerClass}>
						<li>
							<a href={resolve(`/h/${homeId}/rooms`)} onclick={close} class={itemLinkClass}>
								<span class={itemContentClass}>
									<DoorIcon class="h-5 w-5 text-foreground-muted" />
									<span class="text-foreground">Rooms</span>
								</span>
								<ChevronRightIcon class="h-4 w-4 text-foreground-subtle" />
							</a>
						</li>
						<li>
							<a href={resolve(`/h/${homeId}/activity`)} onclick={close} class={itemLinkClass}>
								<span class={itemContentClass}>
									<ClockIcon class="h-5 w-5 text-foreground-muted" />
									<span class="text-foreground">Activity</span>
								</span>
								<ChevronRightIcon class="h-4 w-4 text-foreground-subtle" />
							</a>
						</li>
						<li>
							<a
								href={resolve(`/h/${homeId}/settings/members`)}
								onclick={close}
								class={itemLinkClass}
							>
								<span class={itemContentClass}>
									<UsersIcon class="h-5 w-5 text-foreground-muted" />
									<span class="text-foreground">Members</span>
								</span>
								<ChevronRightIcon class="h-4 w-4 text-foreground-subtle" />
							</a>
						</li>
						<li>
							<a href={resolve(`/h/${homeId}/settings`)} onclick={close} class={itemLinkClass}>
								<span class={itemContentClass}>
									<SettingsIcon class="h-5 w-5 text-foreground-muted" />
									<span class="text-foreground">Home Settings</span>
								</span>
								<ChevronRightIcon class="h-4 w-4 text-foreground-subtle" />
							</a>
						</li>
					</ul>
				{/if}

				<!-- General Section -->
				<h3 class={sectionTitleClass}>General</h3>
				<ul class={listContainerClass}>
					<li>
						<a href={resolve('/settings/gateways')} onclick={close} class={itemLinkClass}>
							<span class={itemContentClass}>
								<GateIcon class="h-5 w-5 text-foreground-muted" />
								<span class="text-foreground">Gateways</span>
							</span>
							<ChevronRightIcon class="h-4 w-4 text-foreground-subtle" />
						</a>
					</li>
					<li>
						<a href={resolve('/settings/preferences')} onclick={close} class={itemLinkClass}>
							<span class={itemContentClass}>
								<SlidersIcon class="h-5 w-5 text-foreground-muted" />
								<span class="text-foreground">Preferences</span>
							</span>
							<ChevronRightIcon class="h-4 w-4 text-foreground-subtle" />
						</a>
					</li>
				</ul>

				<!-- Account Section -->
				<h3 class={sectionTitleClass}>Account</h3>
				<ul class={listContainerClass}>
					<li>
						<a href={resolve('/settings/account')} onclick={close} class={itemLinkClass}>
							<span class={itemContentClass}>
								<UserIcon class="h-5 w-5 text-foreground-muted" />
								<span class="text-foreground">{displayName}</span>
							</span>
							<ChevronRightIcon class="h-4 w-4 text-foreground-subtle" />
						</a>
					</li>
					<li>
						<form method="POST" action={resolve('/logout')} class="contents">
							<button
								type="submit"
								class="flex w-full items-center justify-between px-4 py-3 text-left transition-colors hover:bg-danger-soft group"
							>
								<span class={itemContentClass}>
									<LogoutIcon class="h-5 w-5 text-danger group-hover:text-danger" />
									<span class="text-danger">Sign out</span>
								</span>
							</button>
						</form>
					</li>
				</ul>
			</div>
		</Drawer.Content>
	</Drawer.Portal>
</Drawer.Root>
