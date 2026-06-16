import toast from 'svelte-french-toast';

async function copyToClipboard(
	text: string,
	options?: { onSuccess?: () => void; onError?: () => void }
): Promise<boolean> {
	if (!text || text.trim() === '') {
		options?.onError?.();
		return false;
	}

	try {
		await navigator.clipboard.writeText(text);
		options?.onSuccess?.();
		return true;
	} catch (err) {
		console.error('Failed to copy to clipboard:', err);
		options?.onError?.();
		return false;
	}
}

export async function copy(value: string) {
	await copyToClipboard(value, {
		onSuccess: () => toast.success('Copied to clipboard'),
		onError: () => toast.error('Failed to copy')
	});
}
