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
	let isUpdating = false;

	async function updateDspState(id: string) {
		if (isUpdating) return;
		isUpdating = true;

		try {
			if (!id || id === 'local') {
				hasDsp = false;
				iframeSrc = '';
				showDsp.set(false);
				return;
			}

			const chat = await getChatById(localStorage.token, id);
			const newHasDsp = chat?.meta?.has_dsp || false;
			
			hasDsp = newHasDsp;
			if (hasDsp) {
				// Force iframe refresh by adding timestamp
				iframeSrc = `${WEBUI_BASE_URL}/dsp/?session_id=${id}&_t=${Date.now()}`;
			} else {
				iframeSrc = '';
			}
			showDsp.set(hasDsp);
		} catch (error) {
			console.error('Failed to check DSP status:', error);
			hasDsp = false;
			iframeSrc = '';
			showDsp.set(false);
		} finally {
			isUpdating = false;
		}
	}

	// Watch for chat ID changes and force update
	$: {
		if ($chatId !== currentChatId) {
			currentChatId = $chatId;
			updateDspState($chatId);
		}
	}

	function setupIframeListeners() {
		if (iframeElement?.contentWindow) {
			iframeElement.contentWindow.addEventListener('dragstart', (event) => {
				event.preventDefault();
			});
		}
	}

	onMount(() => {
		// Initial state check
		if ($chatId) {
			currentChatId = $chatId;
			updateDspState($chatId);
		}
	});

	onDestroy(() => {
		showDsp.set(false);
		iframeSrc = '';
		hasDsp = false;
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