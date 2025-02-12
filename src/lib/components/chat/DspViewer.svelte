<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { chatId, showDsp } from '$lib/stores';
	import { getChatById } from '$lib/apis/chats';

	let iframeElement: HTMLIFrameElement & {
		webkitRequestFullscreen?: () => Promise<void>;
		msRequestFullscreen?: () => Promise<void>;
	};

	let iframeSrc = '';
	let hasDsp = false;
	let currentChatId = '';

	async function updateDspState(id: string) {
		if (!id || id === 'local') {
			hasDsp = false;
			showDsp.set(false);
			iframeSrc = '';
			return;
		}

		try {
			const chat = await getChatById(localStorage.token, id);
			hasDsp = chat?.meta?.has_dsp || false;
			showDsp.set(hasDsp);
			
			if (hasDsp) {
				iframeSrc = `${WEBUI_BASE_URL}/dsp/?session_id=${id}`;
			} else {
				iframeSrc = '';
			}
		} catch (error) {
			console.error('Failed to check DSP status:', error);
			hasDsp = false;
			showDsp.set(false);
			iframeSrc = '';
		}
	}

	// Watch for chat ID changes
	$: if ($chatId !== currentChatId) {
		currentChatId = $chatId;
		updateDspState($chatId);
	}

	function setupIframeListeners() {
		if (iframeElement?.contentWindow) {
			iframeElement.contentWindow.addEventListener('dragstart', (event) => {
				event.preventDefault();
			});
		}
	}

	onMount(() => {
		// Check initial state
		updateDspState($chatId);
	});

	onDestroy(() => {
		showDsp.set(false);
	});
</script>

{#if hasDsp && $chatId && $chatId !== 'local'}
	<div class="w-full h-full">
		<iframe
			bind:this={iframeElement}
			title="DSP Viewer"
			src={iframeSrc}
			class="w-full border-0 h-full"
			sandbox="allow-same-origin allow-scripts allow-downloads allow-forms allow-popups allow-popups-to-escape-sandbox allow-modals allow-presentation allow-top-navigation allow-top-navigation-by-user-activation allow-storage-access-by-user-activation"
			allow="downloads *; microphone; camera; display-capture; fullscreen; clipboard-read; clipboard-write"
			on:load={setupIframeListeners}
		/>
	</div>
{/if} 