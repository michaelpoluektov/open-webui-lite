<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { createEventDispatcher, getContext, onDestroy, onMount, tick } from 'svelte';
	const dispatch = createEventDispatcher();

	import { type Model, mobile, models, settings, tools } from '$lib/stores';

	import { findWordIndices } from '$lib/utils';

	import { WEBUI_BASE_URL } from '$lib/constants';

	import RichTextInput from '../common/RichTextInput.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import XMark from '../icons/XMark.svelte';
	import Commands from './MessageInput/Commands.svelte';
	import InputMenu from './MessageInput/InputMenu.svelte';

	const i18n = getContext('i18n');

	export let transparentBackground = false;

	export let onChange: Function = () => {};
	export let createMessagePair: Function;
	export let stopResponse: Function;

	export let autoScroll = false;

	export let atSelectedModel: Model | undefined = undefined;
	export let selectedModels: [''];

	let selectedModelIds = [];
	$: selectedModelIds = atSelectedModel !== undefined ? [atSelectedModel.id] : selectedModels;

	export let history;

	export let prompt = '';
	export let files = [];

	export let selectedToolIds = [];
	export let webSearchEnabled = false;

	$: onChange({
		prompt,
		files,
		selectedToolIds,
		webSearchEnabled
	});

	let loaded = false;
	let recording = false;

	let chatInputElement;

	let filesInputElement;
	let commandsElement;

	let inputFiles;
	let dragged = false;

	export let placeholder = '';

	let visionCapableModels = [];
	$: visionCapableModels = [...(atSelectedModel ? [atSelectedModel] : selectedModels)].filter(
		(model) => $models.find((m) => m.id === model)?.info?.meta?.capabilities?.vision ?? true
	);

	const scrollToBottom = () => {
		const element = document.getElementById('messages-container');
		element.scrollTo({
			top: element.scrollHeight,
			behavior: 'smooth'
		});
	};

	const handleKeyDown = (event: KeyboardEvent) => {
		if (event.key === 'Escape') {
			console.log('Escape');
			dragged = false;
		}
	};

	const onDragOver = (e) => {
		e.preventDefault();

		// Check if a file is being dragged.
		if (e.dataTransfer?.types?.includes('Files')) {
			dragged = true;
		} else {
			dragged = false;
		}
	};

	const onDragLeave = () => {
		dragged = false;
	};

	const onDrop = async (e) => {
		e.preventDefault();
		console.log(e);

		if (e.dataTransfer?.files) {
			const inputFiles = Array.from(e.dataTransfer?.files);
			if (inputFiles && inputFiles.length > 0) {
				console.log(inputFiles);
				inputFilesHandler(inputFiles);
			}
		}

		dragged = false;
	};

	onMount(async () => {
		loaded = true;

		window.setTimeout(() => {
			const chatInput = document.getElementById('chat-input');
			chatInput?.focus();
		}, 0);

		window.addEventListener('keydown', handleKeyDown);

		await tick();

		const dropzoneElement = document.getElementById('chat-container');

		dropzoneElement?.addEventListener('dragover', onDragOver);
		dropzoneElement?.addEventListener('drop', onDrop);
		dropzoneElement?.addEventListener('dragleave', onDragLeave);
	});

	onDestroy(() => {
		console.log('destroy');
		window.removeEventListener('keydown', handleKeyDown);

		const dropzoneElement = document.getElementById('chat-container');

		if (dropzoneElement) {
			dropzoneElement?.removeEventListener('dragover', onDragOver);
			dropzoneElement?.removeEventListener('drop', onDrop);
			dropzoneElement?.removeEventListener('dragleave', onDragLeave);
		}
	});
</script>

{#if loaded}
	<div class="w-full font-primary">
		<div class=" mx-auto inset-x-0 bg-transparent flex justify-center">
			<div
				class="flex flex-col px-3 {($settings?.widescreenMode ?? null)
					? 'max-w-full'
					: 'max-w-6xl'} w-full"
			>
				<div class="relative">
					{#if autoScroll === false && history?.currentId}
						<div
							class=" absolute -top-12 left-0 right-0 flex justify-center z-30 pointer-events-none"
						>
							<button
								class=" bg-white border border-gray-100 dark:border-none dark:bg-white/20 p-1.5 rounded-full pointer-events-auto"
								on:click={() => {
									autoScroll = true;
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

				<div class="w-full relative">
					{#if atSelectedModel !== undefined || selectedToolIds.length > 0 || webSearchEnabled}
						<div
							class="px-3 pb-0.5 pt-1.5 text-left w-full flex flex-col absolute bottom-0 left-0 right-0 bg-gradient-to-t from-white dark:from-gray-900 z-10"
						>
							{#if selectedToolIds.length > 0}
								<div class="flex items-center justify-between w-full">
									<div class="flex items-center gap-2.5 text-sm dark:text-gray-500">
										<div class="pl-1">
											<span class="relative flex size-2">
												<span
													class="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"
												/>
												<span class="relative inline-flex rounded-full size-2 bg-yellow-500" />
											</span>
										</div>
										<div class=" translate-y-[0.5px] text-ellipsis line-clamp-1 flex">
											{#each selectedToolIds.map((id) => {
												return $tools ? $tools.find((t) => t.id === id) : { id: id, name: id };
											}) as tool, toolIdx (toolIdx)}
												<Tooltip
													content={tool?.meta?.description ?? ''}
													className=" {toolIdx !== 0 ? 'pl-0.5' : ''} flex-shrink-0"
													placement="top"
												>
													{tool.name}
												</Tooltip>

												{#if toolIdx !== selectedToolIds.length - 1}
													<span>, </span>
												{/if}
											{/each}
										</div>
									</div>
								</div>
							{/if}

							{#if webSearchEnabled}
								<div class="flex items-center justify-between w-full">
									<div class="flex items-center gap-2.5 text-sm dark:text-gray-500">
										<div class="pl-1">
											<span class="relative flex size-2">
												<span
													class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"
												/>
												<span class="relative inline-flex rounded-full size-2 bg-green-500" />
											</span>
										</div>
										<div class=" translate-y-[0.5px]">{$i18n.t('Search the web')}</div>
									</div>
								</div>
							{/if}

							{#if atSelectedModel !== undefined}
								<div class="flex items-center justify-between w-full">
									<div class="pl-[1px] flex items-center gap-2 text-sm dark:text-gray-500">
										<img
											crossorigin="anonymous"
											alt="model profile"
											class="size-3.5 max-w-[28px] object-cover rounded-full"
											src={$models.find((model) => model.id === atSelectedModel.id)?.info?.meta
												?.profile_image_url ??
												($i18n.language === 'dg-DG'
													? `/doge.png`
													: `${WEBUI_BASE_URL}/static/favicon.png`)}
										/>
										<div class="translate-y-[0.5px]">
											Talking to <span class=" font-medium">{atSelectedModel.name}</span>
										</div>
									</div>
									<div>
										<button
											class="flex items-center dark:text-gray-500"
											on:click={() => {
												atSelectedModel = undefined;
											}}
										>
											<XMark />
										</button>
									</div>
								</div>
							{/if}
						</div>
					{/if}

					<Commands
						bind:this={commandsElement}
						bind:prompt
						bind:files
						on:upload={(e) => {
							dispatch('upload', e.detail);
						}}
						on:select={(e) => {
							const data = e.detail;

							if (data?.type === 'model') {
								atSelectedModel = data.data;
							}

							const chatInputElement = document.getElementById('chat-input');
							chatInputElement?.focus();
						}}
					/>
				</div>
			</div>
		</div>

		<div class="{transparentBackground ? 'bg-transparent' : 'bg-white dark:bg-gray-900'} ">
			<div
				class="{($settings?.widescreenMode ?? null)
					? 'max-w-full'
					: 'max-w-6xl'} px-2.5 mx-auto inset-x-0"
			>
				<div class="">
					<input
						bind:this={filesInputElement}
						bind:files={inputFiles}
						type="file"
						hidden
						multiple
						on:change={async () => {
							if (inputFiles && inputFiles.length > 0) {
								const _inputFiles = Array.from(inputFiles);
								inputFilesHandler(_inputFiles);
							} else {
								toast.error($i18n.t(`File not found.`));
							}

							filesInputElement.value = '';
						}}
					/>

					<form
						class="w-full flex gap-1.5"
						on:submit|preventDefault={() => {
							// check if selectedModels support image input
							dispatch('submit', prompt);
						}}
					>
						<div
							class="flex-1 flex flex-col relative w-full rounded-3xl px-1 bg-gray-600/5 dark:bg-gray-400/5 dark:text-gray-100"
							dir={$settings?.chatDirection ?? 'LTR'}
						>
							<div class=" flex">
								<div class="ml-1 self-end mb-1.5 flex space-x-1">
									<InputMenu
										bind:selectedToolIds
										onClose={async () => {
											await tick();

											const chatInput = document.getElementById('chat-input');
											chatInput?.focus();
										}}
									>
										<button
											class="bg-transparent hover:bg-white/80 text-gray-800 dark:text-white dark:hover:bg-gray-800 transition rounded-full p-2 outline-none focus:outline-none"
											type="button"
											aria-label="More"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												viewBox="0 0 20 20"
												fill="currentColor"
												class="size-5"
											>
												<path
													d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z"
												/>
											</svg>
										</button>
									</InputMenu>
								</div>

								{#if $settings?.richTextInput ?? true}
									<div
										class="scrollbar-hidden text-left bg-transparent dark:text-gray-100 outline-none w-full py-2.5 px-1 rounded-xl resize-none h-fit max-h-80 overflow-auto"
									>
										<RichTextInput
											bind:this={chatInputElement}
											bind:value={prompt}
											id="chat-input"
											messageInput={true}
											shiftEnter={!$mobile ||
												!(
													'ontouchstart' in window ||
													navigator.maxTouchPoints > 0 ||
													navigator.msMaxTouchPoints > 0
												)}
											placeholder={placeholder ? placeholder : $i18n.t('Send a Message')}
											on:keydown={async (e) => {
												e = e.detail.event;

												const isCtrlPressed = e.ctrlKey || e.metaKey; // metaKey is for Cmd key on Mac
												const commandsContainerElement =
													document.getElementById('commands-container');

												if (e.key === 'Escape') {
													stopResponse();
												}

												// Command/Ctrl + Shift + Enter to submit a message pair
												if (isCtrlPressed && e.key === 'Enter' && e.shiftKey) {
													e.preventDefault();
													createMessagePair(prompt);
												}

												// Check if Ctrl + R is pressed
												if (prompt === '' && isCtrlPressed && e.key.toLowerCase() === 'r') {
													e.preventDefault();
													console.log('regenerate');

													const regenerateButton = [
														...document.getElementsByClassName('regenerate-response-button')
													]?.at(-1);

													regenerateButton?.click();
												}

												if (prompt === '' && e.key == 'ArrowUp') {
													e.preventDefault();

													const userMessageElement = [
														...document.getElementsByClassName('user-message')
													]?.at(-1);

													if (userMessageElement) {
														userMessageElement.scrollIntoView({ block: 'center' });
														const editButton = [
															...document.getElementsByClassName('edit-user-message-button')
														]?.at(-1);

														editButton?.click();
													}
												}

												if (commandsContainerElement) {
													if (commandsContainerElement && e.key === 'ArrowUp') {
														e.preventDefault();
														commandsElement.selectUp();

														const commandOptionButton = [
															...document.getElementsByClassName('selected-command-option-button')
														]?.at(-1);
														commandOptionButton.scrollIntoView({ block: 'center' });
													}

													if (commandsContainerElement && e.key === 'ArrowDown') {
														e.preventDefault();
														commandsElement.selectDown();

														const commandOptionButton = [
															...document.getElementsByClassName('selected-command-option-button')
														]?.at(-1);
														commandOptionButton.scrollIntoView({ block: 'center' });
													}

													if (commandsContainerElement && e.key === 'Tab') {
														e.preventDefault();

														const commandOptionButton = [
															...document.getElementsByClassName('selected-command-option-button')
														]?.at(-1);

														commandOptionButton?.click();
													}

													if (commandsContainerElement && e.key === 'Enter') {
														e.preventDefault();

														const commandOptionButton = [
															...document.getElementsByClassName('selected-command-option-button')
														]?.at(-1);

														if (commandOptionButton) {
															commandOptionButton?.click();
														} else {
															document.getElementById('send-message-button')?.click();
														}
													}
												} else {
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

														// Submit the prompt when Enter key is pressed
														if (prompt !== '' && e.keyCode === 13 && !e.shiftKey) {
															dispatch('submit', prompt);
														}
													}
												}

												if (e.key === 'Escape') {
													console.log('Escape');
													atSelectedModel = undefined;
													selectedToolIds = [];
													webSearchEnabled = false;
												}
											}}
											on:paste={async (e) => {
												e = e.detail.event;
												console.log(e);

												const clipboardData = e.clipboardData || window.clipboardData;

												if (clipboardData && clipboardData.items) {
													for (const item of clipboardData.items) {
														if (item.type.indexOf('image') !== -1) {
															const blob = item.getAsFile();
															const reader = new FileReader();

															reader.onload = function (e) {
																files = [
																	...files,
																	{
																		type: 'image',
																		url: `${e.target.result}`
																	}
																];
															};

															reader.readAsDataURL(blob);
														}
													}
												}
											}}
										/>
									</div>
								{:else}
									<textarea
										id="chat-input"
										bind:this={chatInputElement}
										class="scrollbar-hidden bg-transparent dark:text-gray-100 outline-none w-full py-3 px-1 rounded-xl resize-none h-[48px]"
										placeholder={placeholder ? placeholder : $i18n.t('Send a Message')}
										bind:value={prompt}
										on:keypress={(e) => {
											if (
												!$mobile ||
												!(
													'ontouchstart' in window ||
													navigator.maxTouchPoints > 0 ||
													navigator.msMaxTouchPoints > 0
												)
											) {
												// Prevent Enter key from creating a new line
												if (e.key === 'Enter' && !e.shiftKey) {
													e.preventDefault();
												}

												// Submit the prompt when Enter key is pressed
												if (prompt !== '' && e.key === 'Enter' && !e.shiftKey) {
													dispatch('submit', prompt);
												}
											}
										}}
										on:keydown={async (e) => {
											const isCtrlPressed = e.ctrlKey || e.metaKey; // metaKey is for Cmd key on Mac
											const commandsContainerElement =
												document.getElementById('commands-container');

											if (e.key === 'Escape') {
												stopResponse();
											}
											// Command/Ctrl + Shift + Enter to submit a message pair
											if (isCtrlPressed && e.key === 'Enter' && e.shiftKey) {
												e.preventDefault();
												createMessagePair(prompt);
											}

											// Check if Ctrl + R is pressed
											if (prompt === '' && isCtrlPressed && e.key.toLowerCase() === 'r') {
												e.preventDefault();
												console.log('regenerate');

												const regenerateButton = [
													...document.getElementsByClassName('regenerate-response-button')
												]?.at(-1);

												regenerateButton?.click();
											}

											if (prompt === '' && e.key == 'ArrowUp') {
												e.preventDefault();

												const userMessageElement = [
													...document.getElementsByClassName('user-message')
												]?.at(-1);

												const editButton = [
													...document.getElementsByClassName('edit-user-message-button')
												]?.at(-1);

												console.log(userMessageElement);

												userMessageElement.scrollIntoView({ block: 'center' });
												editButton?.click();
											}

											if (commandsContainerElement && e.key === 'ArrowUp') {
												e.preventDefault();
												commandsElement.selectUp();

												const commandOptionButton = [
													...document.getElementsByClassName('selected-command-option-button')
												]?.at(-1);
												commandOptionButton.scrollIntoView({ block: 'center' });
											}

											if (commandsContainerElement && e.key === 'ArrowDown') {
												e.preventDefault();
												commandsElement.selectDown();

												const commandOptionButton = [
													...document.getElementsByClassName('selected-command-option-button')
												]?.at(-1);
												commandOptionButton.scrollIntoView({ block: 'center' });
											}

											if (commandsContainerElement && e.key === 'Enter') {
												e.preventDefault();

												const commandOptionButton = [
													...document.getElementsByClassName('selected-command-option-button')
												]?.at(-1);

												if (e.shiftKey) {
													prompt = `${prompt}\n`;
												} else if (commandOptionButton) {
													commandOptionButton?.click();
												} else {
													document.getElementById('send-message-button')?.click();
												}
											}

											if (commandsContainerElement && e.key === 'Tab') {
												e.preventDefault();

												const commandOptionButton = [
													...document.getElementsByClassName('selected-command-option-button')
												]?.at(-1);

												commandOptionButton?.click();
											} else if (e.key === 'Tab') {
												const words = findWordIndices(prompt);

												if (words.length > 0) {
													const word = words.at(0);
													const fullPrompt = prompt;

													prompt = prompt.substring(0, word?.endIndex + 1);
													await tick();

													e.target.scrollTop = e.target.scrollHeight;
													prompt = fullPrompt;
													await tick();

													e.preventDefault();
													e.target.setSelectionRange(word?.startIndex, word.endIndex + 1);
												}

												e.target.style.height = '';
												e.target.style.height = Math.min(e.target.scrollHeight, 320) + 'px';
											}

											if (e.key === 'Escape') {
												console.log('Escape');
												atSelectedModel = undefined;
												selectedToolIds = [];
												webSearchEnabled = false;
											}
										}}
										rows="1"
										on:input={async (e) => {
											e.target.style.height = '';
											e.target.style.height = Math.min(e.target.scrollHeight, 320) + 'px';
										}}
										on:focus={async (e) => {
											e.target.style.height = '';
											e.target.style.height = Math.min(e.target.scrollHeight, 320) + 'px';
										}}
										on:paste={async (e) => {
											const clipboardData = e.clipboardData || window.clipboardData;

											if (clipboardData && clipboardData.items) {
												for (const item of clipboardData.items) {
													if (item.type.indexOf('image') !== -1) {
														const blob = item.getAsFile();
														const reader = new FileReader();

														reader.onload = function (e) {
															files = [
																...files,
																{
																	type: 'image',
																	url: `${e.target.result}`
																}
															];
														};

														reader.readAsDataURL(blob);
													}
												}
											}
										}}
									/>
								{/if}

								<div class="self-end mb-1.5 flex space-x-1 mr-1">
									{#if !history?.currentId || history.messages[history.currentId]?.done == true}
										<Tooltip content={$i18n.t('Record voice')}>
											<button
												id="voice-input-button"
												class=" text-gray-600 dark:text-gray-300 hover:text-gray-700 dark:hover:text-gray-200 transition rounded-full p-1.5 mr-0.5 self-center"
												type="button"
												on:click={async () => {
													try {
														let stream = await navigator.mediaDevices
															.getUserMedia({ audio: true })
															.catch(function (err) {
																toast.error(
																	$i18n.t(
																		`Permission denied when accessing microphone: {{error}}`,
																		{
																			error: err
																		}
																	)
																);
																return null;
															});

														if (stream) {
															recording = true;
															const tracks = stream.getTracks();
															tracks.forEach((track) => track.stop());
														}
														stream = null;
													} catch {
														toast.error($i18n.t('Permission denied when accessing microphone'));
													}
												}}
												aria-label="Voice Input"
											>
												<svg
													xmlns="http://www.w3.org/2000/svg"
													viewBox="0 0 20 20"
													fill="currentColor"
													class="w-5 h-5 translate-y-[0.5px]"
												>
													<path d="M7 4a3 3 0 016 0v6a3 3 0 11-6 0V4z" />
													<path
														d="M5.5 9.643a.75.75 0 00-1.5 0V10c0 3.06 2.29 5.585 5.25 5.954V17.5h-1.5a.75.75 0 000 1.5h4.5a.75.75 0 000-1.5h-1.5v-1.546A6.001 6.001 0 0016 10v-.357a.75.75 0 00-1.5 0V10a4.5 4.5 0 01-9 0v-.357z"
													/>
												</svg>
											</button>
										</Tooltip>
									{/if}

									{#if !history.currentId || history.messages[history.currentId]?.done == true}
										{#if prompt === ''}
											<div class=" flex items-center"></div>
										{:else}
											<div class=" flex items-center">
												<Tooltip content={$i18n.t('Send message')}>
													<button
														id="send-message-button"
														class="{prompt !== ''
															? 'bg-black text-white hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100 '
															: 'text-white bg-gray-200 dark:text-gray-900 dark:bg-gray-700 disabled'} transition rounded-full p-1.5 self-center"
														type="submit"
														disabled={prompt === ''}
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
										{/if}
									{:else}
										<div class=" flex items-center">
											<Tooltip content={$i18n.t('Stop')}>
												<button
													class="bg-white hover:bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-800 transition rounded-full p-1.5"
													on:click={() => {
														stopResponse();
													}}
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														viewBox="0 0 24 24"
														fill="currentColor"
														class="size-6"
													>
														<path
															fill-rule="evenodd"
															d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm6-2.438c0-.724.588-1.312 1.313-1.312h4.874c.725 0 1.313.588 1.313 1.313v4.874c0 .725-.588 1.313-1.313 1.313H9.564a1.312 1.312 0 01-1.313-1.313V9.564z"
															clip-rule="evenodd"
														/>
													</svg>
												</button>
											</Tooltip>
										</div>
									{/if}
								</div>
							</div>
						</div>
					</form>
				</div>
			</div>
		</div>
	</div>
{/if}
