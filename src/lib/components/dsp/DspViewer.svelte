<script lang="ts">
	import { onMount, createEventDispatcher } from 'svelte';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import XMark from '../icons/XMark.svelte';
	import ArrowsPointingOut from '../icons/ArrowsPointingOut.svelte';
	import Tooltip from '../common/Tooltip.svelte';

	const dispatch = createEventDispatcher();

	let iframeElement: HTMLIFrameElement & {
		webkitRequestFullscreen?: () => Promise<void>;
		msRequestFullscreen?: () => Promise<void>;
	};

	const showFullScreen = () => {
		if (iframeElement.requestFullscreen) {
			iframeElement.requestFullscreen();
		} else if (iframeElement.webkitRequestFullscreen) {
			iframeElement.webkitRequestFullscreen();
		} else if (iframeElement.msRequestFullscreen) {
			iframeElement.msRequestFullscreen();
		}
	};

	onMount(() => {
		// Prevent iframe from capturing drag events
		iframeElement.contentWindow?.addEventListener('mouseenter', function (e) {
			e.preventDefault();
			iframeElement.contentWindow?.addEventListener('dragstart', (event) => {
				event.preventDefault();
			});
		});
	});
</script>

<div class="w-full h-full relative flex flex-col bg-gray-50 dark:bg-gray-850">
	<div class="w-full h-full flex-1 relative">
		<div class="absolute pointer-events-none z-50 w-full flex items-center justify-end p-4">
			<button
				class="self-center pointer-events-auto p-1 rounded-full bg-white dark:bg-gray-850"
				on:click={() => {
					dispatch('close');
				}}
			>
				<XMark className="size-3.5 text-gray-900 dark:text-white" />
			</button>
		</div>

		<div class="flex-1 w-full h-full">
			<iframe
				bind:this={iframeElement}
				title="DSP Viewer"
				src={`${WEBUI_BASE_URL}/dsp/`}
				class="w-full border-0 h-full rounded-none"
				sandbox="allow-scripts allow-forms allow-same-origin"
			/>
		</div>
	</div>

	<div class="flex justify-end items-center p-2.5 font-primary text-gray-900 dark:text-white">
		<Tooltip content="Open in full screen">
			<button
				class="bg-none border-none text-xs bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md p-0.5"
				on:click={showFullScreen}
			>
				<ArrowsPointingOut className="size-3.5" />
			</button>
		</Tooltip>
	</div>
</div>
