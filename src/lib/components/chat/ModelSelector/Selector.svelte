<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { marked } from 'marked';
	import Fuse from 'fuse.js';

	import { flyAndScale } from '$lib/utils/transitions';
	import { createEventDispatcher, onMount, getContext, tick } from 'svelte';

	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import Check from '$lib/components/icons/Check.svelte';

	import { user, mobile, temporaryChatEnabled } from '$lib/stores';
	import { toast } from 'svelte-sonner';
	import { sanitizeResponseContent } from '$lib/utils';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import ChatBubbleOval from '$lib/components/icons/ChatBubbleOval.svelte';
	import { goto } from '$app/navigation';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let id = '';
	export let value = '';
	export let placeholder = 'Select a model';

	export let showTemporaryChatControl = false;

	export let items: {
		label: string;
		value: string;
		model: Model;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		[key: string]: any;
	}[] = [];

	export let className = 'w-[32rem]';
	export let triggerClassName = 'text-lg';

	let show = false;

	let selectedModel = '';
	$: selectedModel = items.find((item) => item.value === value) ?? '';

	let searchValue = '';

	let selectedModelIdx = 0;

	const fuse = new Fuse(
		items.map((item) => {
			const _item = {
				...item,
				modelName: item.model?.name,
				tags: item.model?.info?.meta?.tags?.map((tag) => tag.name).join(' '),
				desc: item.model?.info?.meta?.description
			};
			return _item;
		}),
		{
			keys: ['value', 'tags', 'modelName'],
			threshold: 0.4
		}
	);

	$: filteredItems = searchValue
		? fuse.search(searchValue).map((e) => {
				return e.item;
			})
		: items;

	onMount(async () => {});
</script>

<DropdownMenu.Root
	bind:open={show}
	onOpenChange={async () => {
		searchValue = '';
		selectedModelIdx = 0;
		window.setTimeout(() => document.getElementById('model-search-input')?.focus(), 0);
	}}
	closeFocus={false}
>
	<DropdownMenu.Trigger
		class="relative w-full font-primary"
		aria-label={placeholder}
		id="model-selector-{id}-button"
	>
		<div
			class="flex w-full text-left px-0.5 outline-none bg-transparent truncate {triggerClassName} justify-between font-medium placeholder-gray-400 focus:outline-none"
		>
			{#if selectedModel}
				{selectedModel.label}
			{:else}
				{placeholder}
			{/if}
			<ChevronDown className=" self-center ml-2 size-3" strokeWidth="2.5" />
		</div>
	</DropdownMenu.Trigger>

	<DropdownMenu.Content
		class=" z-40 {$mobile
			? `w-full`
			: `${className}`} max-w-[calc(100vw-1rem)] justify-start rounded-xl  bg-white dark:bg-gray-850 dark:text-white shadow-lg  outline-none"
		transition={flyAndScale}
		side={$mobile ? 'bottom' : 'bottom-start'}
		sideOffset={3}
	>
		<slot>
			<div class="px-3 my-2 max-h-64 overflow-y-auto scrollbar-hidden group">
				{#each filteredItems as item, index}
					<button
						aria-label="model-item"
						class="flex w-full text-left font-medium line-clamp-1 select-none items-center rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-none transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg cursor-pointer data-[highlighted]:bg-muted {index ===
						selectedModelIdx
							? 'bg-gray-100 dark:bg-gray-800 group-hover:bg-transparent'
							: ''}"
						data-arrow-selected={index === selectedModelIdx}
						on:click={() => {
							value = item.value;
							selectedModelIdx = index;

							show = false;
						}}
					>
						<div class="flex flex-col">
							{#if $mobile && (item?.model?.info?.meta?.tags ?? []).length > 0}
								<div class="flex gap-0.5 self-start h-full mb-1.5 -translate-x-1">
									{#each item.model?.info?.meta.tags as tag}
										<div
											class=" text-xs font-bold px-1 rounded uppercase line-clamp-1 bg-gray-500/20 text-gray-700 dark:text-gray-200"
										>
											{tag.name}
										</div>
									{/each}
								</div>
							{/if}
							<div class="flex items-center gap-2">
								<div class="flex items-center min-w-fit">
									<div class="line-clamp-1">
										<div class="flex items-center min-w-fit">
											<Tooltip
												content={$user?.role === 'admin' ? (item?.value ?? '') : ''}
												placement="top-start"
											>
												<img
													src={item.model?.info?.meta?.profile_image_url ?? '/static/favicon.png'}
													alt="Model"
													class="rounded-full size-5 flex items-center mr-2"
												/>
												{item.label}
											</Tooltip>
										</div>
									</div>
								</div>

								<!-- {JSON.stringify(item.info)} -->

								{#if item.model.owned_by === 'openai'}
									<Tooltip content={`${'External'}`}>
										<div class="translate-y-[1px]">
											<svg
												xmlns="http://www.w3.org/2000/svg"
												viewBox="0 0 16 16"
												fill="currentColor"
												class="size-3"
											>
												<path
													fill-rule="evenodd"
													d="M8.914 6.025a.75.75 0 0 1 1.06 0 3.5 3.5 0 0 1 0 4.95l-2 2a3.5 3.5 0 0 1-5.396-4.402.75.75 0 0 1 1.251.827 2 2 0 0 0 3.085 2.514l2-2a2 2 0 0 0 0-2.828.75.75 0 0 1 0-1.06Z"
													clip-rule="evenodd"
												/>
												<path
													fill-rule="evenodd"
													d="M7.086 9.975a.75.75 0 0 1-1.06 0 3.5 3.5 0 0 1 0-4.95l2-2a3.5 3.5 0 0 1 5.396 4.402.75.75 0 0 1-1.251-.827 2 2 0 0 0-3.085-2.514l-2 2a2 2 0 0 0 0 2.828.75.75 0 0 1 0 1.06Z"
													clip-rule="evenodd"
												/>
											</svg>
										</div>
									</Tooltip>
								{/if}

								{#if item.model?.info?.meta?.description}
									<Tooltip
										content={`${marked.parse(
											sanitizeResponseContent(item.model?.info?.meta?.description).replaceAll(
												'\n',
												'<br>'
											)
										)}`}
									>
										<div class=" translate-y-[1px]">
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
												stroke-width="1.5"
												stroke="currentColor"
												class="w-4 h-4"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"
												/>
											</svg>
										</div>
									</Tooltip>
								{/if}

								{#if !$mobile && (item?.model?.info?.meta?.tags ?? []).length > 0}
									<div class="flex gap-0.5 self-center items-center h-full translate-y-[0.5px]">
										{#each item.model?.info?.meta.tags as tag}
											<Tooltip content={tag.name}>
												<div
													class=" text-xs font-bold px-1 rounded uppercase line-clamp-1 bg-gray-500/20 text-gray-700 dark:text-gray-200"
												>
													{tag.name}
												</div>
											</Tooltip>
										{/each}
									</div>
								{/if}
							</div>
						</div>

						{#if value === item.value}
							<div class="ml-auto pl-2 pr-2 md:pr-0">
								<Check />
							</div>
						{/if}
					</button>
				{:else}
					<div>
						<div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
							{$i18n.t('No results found')}
						</div>
					</div>
				{/each}
			</div>

			{#if showTemporaryChatControl}
				<hr class="border-gray-50 dark:border-gray-800" />

				<div class="flex items-center mx-2 my-2">
					<button
						class="flex justify-between w-full font-medium line-clamp-1 select-none items-center rounded-button py-2 px-3 text-sm text-gray-700 dark:text-gray-100 outline-none transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg cursor-pointer data-[highlighted]:bg-muted"
						on:click={async () => {
							temporaryChatEnabled.set(!$temporaryChatEnabled);
							await goto('/');
							const newChatButton = document.getElementById('new-chat-button');
							setTimeout(() => {
								newChatButton?.click();
							}, 0);

							// add 'temporary-chat=true' to the URL
							if ($temporaryChatEnabled) {
								history.replaceState(null, '', '?temporary-chat=true');
							} else {
								history.replaceState(null, '', location.pathname);
							}

							show = false;
						}}
					>
						<div class="flex gap-2.5 items-center">
							<ChatBubbleOval className="size-4" strokeWidth="2.5" />

							{$i18n.t(`Temporary Chat`)}
						</div>

						<div>
							<Switch state={$temporaryChatEnabled} />
						</div>
					</button>
				</div>
			{/if}

			<div class="hidden w-[42rem]" />
			<div class="hidden w-[32rem]" />
		</slot>
	</DropdownMenu.Content>
</DropdownMenu.Root>
