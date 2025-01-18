<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	import { prompts } from '$lib/stores';

	import { removeLastWordFromString } from '$lib/utils';
	import { getPrompts } from '$lib/apis/prompts';

	import Prompts from './Commands/Prompts.svelte';
	import Models from './Commands/Models.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	export let prompt = '';

	let loading = false;
	let commandElement = null;

	export const selectUp = () => {
		commandElement?.selectUp();
	};

	export const selectDown = () => {
		commandElement?.selectDown();
	};

	let command = '';
	$: command = prompt?.split('\n').pop()?.split(' ')?.pop() ?? '';

	let show = false;
	$: show = ['/', '#', '@'].includes(command?.charAt(0)) || '\\#' === command.slice(0, 2);

	$: if (show) {
		init();
	}

	const init = async () => {
		loading = true;
		await Promise.all([
			(async () => {
				prompts.set(await getPrompts(localStorage.token));
			})()
		]);
		loading = false;
	};
</script>

{#if show}
	{#if !loading}
		{#if command?.charAt(0) === '/'}
			<Prompts bind:this={commandElement} bind:prompt {command} />
		{:else if command?.charAt(0) === '@'}
			<Models
				bind:this={commandElement}
				{command}
				on:select={(e) => {
					prompt = removeLastWordFromString(prompt, command);

					dispatch('select', {
						type: 'model',
						data: e.detail
					});
				}}
			/>
		{/if}
	{:else}
		<div
			id="commands-container"
			class="px-2 mb-2 text-left w-full absolute bottom-0 left-0 right-0 z-10"
		>
			<div class="flex w-full rounded-xl border border-gray-50 dark:border-gray-850">
				<div
					class="max-h-60 flex flex-col w-full rounded-xl bg-white dark:bg-gray-900 dark:text-gray-100"
				>
					<Spinner />
				</div>
			</div>
		</div>
	{/if}
{/if}
