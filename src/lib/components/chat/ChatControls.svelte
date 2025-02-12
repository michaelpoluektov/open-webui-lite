<script lang="ts">
	import { SvelteFlowProvider } from '@xyflow/svelte';
	import { Pane, PaneResizer } from 'paneforge';

	import { onDestroy, onMount, tick } from 'svelte';
	import { showControls, showOverview, showArtifacts } from '$lib/stores';

	import Controls from './Controls/Controls.svelte';
	import Drawer from '../common/Drawer.svelte';
	import Overview from './Overview.svelte';
	import EllipsisVertical from '../icons/EllipsisVertical.svelte';
	import Artifacts from './Artifacts.svelte';

	export let history: any;
	export let models: any[] = [];
	export let chatId: string | null = null;
	export let params: Record<string, any> = {};
	export let showMessage: Function;
	export let pane: any;

	let mediaQuery: MediaQueryList;
	let largeScreen = false;
	let dragged = false;
	let minSize = 0;

	export const openPane = () => {
		if (parseInt(localStorage?.chatControlsSize)) {
			pane.resize(parseInt(localStorage?.chatControlsSize));
		} else {
			pane.resize(minSize);
		}
	};

	const handleMediaQuery = async (e: MediaQueryListEvent) => {
		if (e.matches) {
			largeScreen = true;
		} else {
			largeScreen = false;
			pane = null;
		}
	};

	const onMouseDown = (event: MouseEvent) => {
		dragged = true;
	};

	const onMouseUp = (event: MouseEvent) => {
		if (dragged) {
			localStorage.chatControlsSize = pane.size;
			dragged = false;
		}
	};

	onMount(() => {
		mediaQuery = window.matchMedia('(min-width: 1024px)');
		mediaQuery.addEventListener('change', handleMediaQuery);
		handleMediaQuery(mediaQuery as unknown as MediaQueryListEvent);

		const container = document.getElementById('chat-controls');
		if (!container) return;

		const resizeObserver = new ResizeObserver((entries) => {
			for (const entry of entries) {
				minSize = entry.contentRect.width;
			}
		});

		// Start observing the container's size changes
		resizeObserver.observe(container);

		document.addEventListener('mousedown', onMouseDown);
		document.addEventListener('mouseup', onMouseUp);
	});

	onDestroy(() => {
		showControls.set(false);

		if (mediaQuery) {
			mediaQuery.removeEventListener('change', handleMediaQuery);
		}
		document.removeEventListener('mousedown', onMouseDown);
		document.removeEventListener('mouseup', onMouseUp);
	});

	const closeHandler = () => {
		showControls.set(false);
		showOverview.set(false);
		showArtifacts.set(false);
	};

	$: if (!chatId) {
		closeHandler();
	}
</script>

<SvelteFlowProvider>
	{#if !largeScreen}
		{#if $showControls}
			<Drawer
				show={$showControls}
				on:close={() => {
					showControls.set(false);
				}}
			></Drawer>
		{/if}
	{:else}
		<!-- if $showControls -->

		{#if $showControls}
			<PaneResizer class="relative flex w-2 items-center justify-center bg-background group">
				<div class="z-10 flex h-7 w-5 items-center justify-center rounded-sm">
					<EllipsisVertical className="size-4 invisible group-hover:visible" />
				</div>
			</PaneResizer>
		{/if}

		<Pane
			bind:pane
			defaultSize={0}
			onResize={(size) => {
				console.log('size', size, minSize);

				if ($showControls && pane.isExpanded()) {
					if (size < minSize) {
						pane.resize(minSize);
					}

					if (size < minSize) {
						localStorage.chatControlsSize = 0;
					} else {
						localStorage.chatControlsSize = size;
					}
				}
			}}
			onCollapse={() => {
				showControls.set(false);
			}}
			collapsible={true}
			class="pt-8"
		>
			{#if $showControls}
				<div class="pr-4 pb-8 flex max-h-full min-h-full">
					<div
						class="w-full {$showOverview || $showArtifacts
							? ' '
							: 'px-4 py-4 bg-white dark:shadow-lg dark:bg-gray-850  border border-gray-50 dark:border-gray-850'}  rounded-xl z-40 pointer-events-auto overflow-y-auto scrollbar-hidden"
					>
						{#if $showArtifacts}
							<Artifacts {history} overlay={dragged} />
						{:else if $showOverview}
							<Overview
								{history}
								on:nodeclick={(e) => {
									if (e.detail.node.data.message.favorite) {
										history.messages[e.detail.node.data.message.id].favorite = true;
									} else {
										history.messages[e.detail.node.data.message.id].favorite = null;
									}

									showMessage(e.detail.node.data.message);
								}}
								on:close={() => {
									showControls.set(false);
								}}
							/>
						{:else}
							<Controls
								on:close={() => {
									showControls.set(false);
								}}
								{models}
								bind:params
							/>
						{/if}
					</div>
				</div>
			{/if}
		</Pane>
	{/if}
</SvelteFlowProvider>
