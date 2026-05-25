export async function copyToClipboard(
	text: string,
	options?: { onSuccess?: () => void; onError?: () => void }
): Promise<boolean> {
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

