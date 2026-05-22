// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import type { User } from '$lib/types/auth';
import type { Home } from '$lib/types/home';

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user?: User;
			token?: string;
			homes?: Home[];
			activeHome?: Home | null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
