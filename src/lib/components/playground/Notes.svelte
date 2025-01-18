<script>
	import { getContext } from 'svelte';
	const i18n = getContext('i18n');

	import RichTextInput from '../common/RichTextInput.svelte';
	import Spinner from '../common/Spinner.svelte';
	import { toast } from 'svelte-sonner';

	let name = '';
	let content = '';

	let loading = false;
</script>

<div class="relative flex-1 w-full h-full flex justify-center overflow-auto px-5">
	{#if loading}
		<div class=" absolute top-0 bottom-0 left-0 right-0 flex">
			<div class="m-auto">
				<Spinner />
			</div>
		</div>
	{/if}

	<div class=" w-full flex flex-col gap-2 {loading ? 'opacity-20' : ''}">
		<div class="flex-shrink-0 w-full flex justify-between items-center">
			<div class="w-full">
				<input
					class="w-full text-2xl font-medium bg-transparent outline-none"
					type="text"
					bind:value={name}
					placeholder={$i18n.t('Title')}
					required
				/>
			</div>
		</div>

		<div class=" flex-1 w-full h-full">
			<RichTextInput
				className=" input-prose-sm"
				bind:value={content}
				placeholder={$i18n.t('Write something...')}
			/>
		</div>
	</div>
</div>
