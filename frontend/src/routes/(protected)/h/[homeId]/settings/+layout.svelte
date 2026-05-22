<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const homeId = $derived(data.home.id);
	const pathname = $derived(page.url.pathname);

	const onGeneral = $derived(pathname.endsWith('/settings/general'));
	const onMembers = $derived(pathname.endsWith('/settings/members'));
	const onDanger = $derived(pathname.endsWith('/settings/danger'));

	const tabBase = 'shrink-0 border-b-2 px-4 py-2 text-sm transition-colors';
	const tabActive = 'border-accent text-accent';
	const tabIdle = 'border-transparent text-foreground-muted hover:text-foreground';
</script>

<div class="flex flex-col">
	<h1 class="mb-1 text-2xl">{data.home.name}</h1>
	<p class="mb-4 text-sm text-foreground-muted">Home settings</p>

	<nav
		class="-mx-4 mb-6 flex gap-1 overflow-x-auto border-b border-line px-4"
		aria-label="Settings sections"
	>
		<a
			href={resolve(`/h/${homeId}/settings/general`)}
			class="{tabBase} {onGeneral ? tabActive : tabIdle}"
			aria-current={onGeneral ? 'page' : undefined}
		>
			General
		</a>
		<a
			href={resolve(`/h/${homeId}/settings/members`)}
			class="{tabBase} {onMembers ? tabActive : tabIdle}"
			aria-current={onMembers ? 'page' : undefined}
		>
			Members
		</a>
		<a
			href={resolve(`/h/${homeId}/settings/danger`)}
			class="{tabBase} {onDanger ? tabActive : tabIdle}"
			aria-current={onDanger ? 'page' : undefined}
		>
			Danger
		</a>
	</nav>

	{@render children()}
</div>
