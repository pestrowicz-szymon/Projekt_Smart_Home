<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { HomeIcon, CpuIcon, ZapIcon, GridIcon } from '$lib/components/icons';

	interface Props {
		onMoreClick: () => void;
	}

	let { onMoreClick }: Props = $props();

	const homeId = $derived(page.params.homeId);
	const pathname = $derived(page.url.pathname);

	const onDashboard = $derived(pathname.endsWith('/dashboard'));
	const onDevices = $derived(pathname.includes('/devices'));
	const onAutomations = $derived(pathname.includes('/automations'));

	const tabBase =
		'flex flex-col items-center gap-1 py-2.5 text-xs transition-colors';
	const tabActive = 'text-accent';
	const tabIdle = 'text-foreground-muted hover:text-foreground';
</script>

<nav
	class="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface pb-[env(safe-area-inset-bottom)]"
	aria-label="Primary"
>
	<ul class="mx-auto grid max-w-md grid-cols-4">
		<li class="contents">
			<a
				href={homeId ? resolve(`/h/${homeId}/dashboard`) : resolve('/h')}
				class="{tabBase} {onDashboard ? tabActive : tabIdle}"
				aria-current={onDashboard ? 'page' : undefined}
			>
				<HomeIcon class="h-6 w-6" />
				<span>Home</span>
			</a>
		</li>
		<li class="contents">
			<a
				href={homeId ? resolve(`/h/${homeId}/devices`) : resolve('/h')}
				class="{tabBase} {onDevices ? tabActive : tabIdle}"
				aria-current={onDevices ? 'page' : undefined}
			>
				<CpuIcon class="h-6 w-6" />
				<span>Devices</span>
			</a>
		</li>
		<li class="contents">
			<a
				href={homeId ? resolve(`/h/${homeId}/automations`) : resolve('/h')}
				class="{tabBase} {onAutomations ? tabActive : tabIdle}"
				aria-current={onAutomations ? 'page' : undefined}
			>
				<ZapIcon class="h-6 w-6" />
				<span>Routines</span>
			</a>
		</li>
		<li class="contents">
			<button
				type="button"
				onclick={onMoreClick}
				class="{tabBase} {tabIdle}"
				aria-label="Open more options"
			>
				<GridIcon class="h-6 w-6" />
				<span>More</span>
			</button>
		</li>
	</ul>
</nav>
