<script lang="ts">
	import { getContext, tick } from 'svelte';

	const i18n = getContext('i18n');

	import { mobile, settings } from '$lib/stores';

	import RichTextInput from '../common/RichTextInput.svelte';
	import Tooltip from '../common/Tooltip.svelte';

	export let placeholder = $i18n.t('Send a Message');
	export const transparentBackground = false;

	export let id = null;

	let content = '';

	export let typingUsers = [];

	export let onSubmit: Function;
	export let onChange: Function;
	export let scrollEnd = true;
	export let scrollToBottom: Function = () => {};

	const submitHandler = async () => {
		if (content === '') {
			return;
		}

		onSubmit({
			content
		});

		content = '';

		await tick();

		const chatInputElement = document.getElementById(`chat-input-${id}`);
		chatInputElement?.focus();
	};

	$: if (content) {
		onChange();
	}
</script>

<div class="bg-transparent">
	<div
		class="{($settings?.widescreenMode ?? null)
			? 'max-w-full'
			: 'max-w-6xl'} px-2.5 mx-auto inset-x-0 relative"
	>
		<div class="absolute top-0 left-0 right-0 mx-auto inset-x-0 bg-transparent flex justify-center">
			<div class="flex flex-col px-3 w-full">
				<div class="relative">
					{#if scrollEnd === false}
						<div
							class=" absolute -top-12 left-0 right-0 flex justify-center z-30 pointer-events-none"
						>
							<button
								class=" bg-white border border-gray-100 dark:border-none dark:bg-white/20 p-1.5 rounded-full pointer-events-auto"
								on:click={() => {
									scrollEnd = true;
									scrollToBottom();
								}}
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 20 20"
									fill="currentColor"
									class="w-5 h-5"
								>
									<path
										fill-rule="evenodd"
										d="M10 3a.75.75 0 01.75.75v10.638l3.96-4.158a.75.75 0 111.08 1.04l-5.25 5.5a.75.75 0 01-1.08 0l-5.25-5.5a.75.75 0 111.08-1.04l3.96 4.158V3.75A.75.75 0 0110 3z"
										clip-rule="evenodd"
									/>
								</svg>
							</button>
						</div>
					{/if}
				</div>

				<div class="relative">
					<div class=" -mt-5">
						{#if typingUsers.length > 0}
							<div class=" text-xs px-4 mb-1">
								<span class=" font-normal text-black dark:text-white">
									{typingUsers.map((user) => user.name).join(', ')}
								</span>
								{$i18n.t('is typing...')}
							</div>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<div class="">
			<form
				class="w-full flex gap-1.5"
				on:submit|preventDefault={() => {
					submitHandler();
				}}
			>
				<div
					class="flex-1 flex flex-col relative w-full rounded-3xl px-1 bg-gray-600/5 dark:bg-gray-400/5 dark:text-gray-100"
					dir={$settings?.chatDirection ?? 'LTR'}
				>
					<div class=" flex">
						<div
							class="scrollbar-hidden text-left bg-transparent dark:text-gray-100 outline-none w-full py-2.5 px-1 rounded-xl resize-none h-fit max-h-80 overflow-auto"
						>
							<RichTextInput
								bind:value={content}
								id={`chat-input-${id}`}
								messageInput={true}
								shiftEnter={!$mobile ||
									!(
										'ontouchstart' in window ||
										navigator.maxTouchPoints > 0 ||
										navigator.msMaxTouchPoints > 0
									)}
								{placeholder}
								on:keydown={async (e) => {
									e = e.detail.event;
									if (
										!$mobile ||
										!(
											'ontouchstart' in window ||
											navigator.maxTouchPoints > 0 ||
											navigator.msMaxTouchPoints > 0
										)
									) {
										// Prevent Enter key from creating a new line
										// Uses keyCode '13' for Enter key for chinese/japanese keyboards
										if (e.keyCode === 13 && !e.shiftKey) {
											e.preventDefault();
										}

										// Submit the content when Enter key is pressed
										if (content !== '' && e.keyCode === 13 && !e.shiftKey) {
											submitHandler();
										}
									}

									if (e.key === 'Escape') {
										console.log('Escape');
									}
								}}
								on:paste={async (e) => {
									e = e.detail.event;
									console.log(e);
								}}
							/>
						</div>

						<div class="self-end mb-1.5 flex space-x-1 mr-1">
							<div class=" flex items-center">
								<div class=" flex items-center">
									<Tooltip content={$i18n.t('Send message')}>
										<button
											id="send-message-button"
											class="{content !== ''
												? 'bg-black text-white hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100 '
												: 'text-white bg-gray-200 dark:text-gray-900 dark:bg-gray-700 disabled'} transition rounded-full p-1.5 self-center"
											type="submit"
											disabled={content === ''}
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												viewBox="0 0 16 16"
												fill="currentColor"
												class="size-6"
											>
												<path
													fill-rule="evenodd"
													d="M8 14a.75.75 0 0 1-.75-.75V4.56L4.03 7.78a.75.75 0 0 1-1.06-1.06l4.5-4.5a.75.75 0 0 1 1.06 0l4.5 4.5a.75.75 0 0 1-1.06 1.06L8.75 4.56v8.69A.75.75 0 0 1 8 14Z"
													clip-rule="evenodd"
												/>
											</svg>
										</button>
									</Tooltip>
								</div>
							</div>
						</div>
					</div>
				</div>
			</form>
		</div>
	</div>
</div>
