<script lang="ts">
	import { deleteDB, openDB } from 'idb';
	import { onMount, tick } from 'svelte';
	import { Pane, PaneResizer, PaneGroup } from 'paneforge';

	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	import { getModels } from '$lib/apis';
	import { getBanners } from '$lib/apis/configs';
	import { getTools } from '$lib/apis/tools';
	import { getUserSettings } from '$lib/apis/users';

	import {
		banners,
		models,
		settings,
		showSettings,
		temporaryChatEnabled,
		tools,
		user,
		showDsp
	} from '$lib/stores';

	import SettingsModal from '$lib/components/chat/SettingsModal.svelte';
	import AccountPending from '$lib/components/layout/Overlay/AccountPending.svelte';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import DspViewer from '$lib/components/chat/DspViewer.svelte';
	import EllipsisVertical from '$lib/components/icons/EllipsisVertical.svelte';

	let loaded = false;
	let DB = null;
	let localDBChats = [];

	onMount(async () => {
		if ($user === undefined) {
			await goto('/auth');
		} else if (['user', 'admin'].includes($user.role)) {
			try {
				// Check if IndexedDB exists
				DB = await openDB('Chats', 1);

				if (DB) {
					const chats = await DB.getAllFromIndex('chats', 'timestamp');
					localDBChats = chats.map((_, idx) => chats[chats.length - 1 - idx]);

					if (localDBChats.length === 0) {
						await deleteDB('Chats');
					}
				}

				console.log(DB);
			} catch (error) {
				// IndexedDB Not Found
			}

			const [userSettingsResult, modelsData, bannersData, toolsData] = await Promise.all([
				getUserSettings(localStorage.token).catch((error) => {
					console.error(error);
					return null;
				}),
				getModels(localStorage.token),
				getBanners(localStorage.token),
				getTools(localStorage.token)
			]);

			if (userSettingsResult) {
				settings.set(userSettingsResult.ui);
			} else {
				let localStorageSettings = {} as Parameters<(typeof settings)['set']>[0];

				try {
					localStorageSettings = JSON.parse(localStorage.getItem('settings') ?? '{}');
				} catch (e: unknown) {
					console.error('Failed to parse settings from localStorage', e);
				}

				settings.set(localStorageSettings);
			}

			// Set models, banners, and tools after all promises resolve
			models.set(modelsData);
			banners.set(bannersData);
			tools.set(toolsData);

			document.addEventListener('keydown', async function (event) {
				const isCtrlPressed = event.ctrlKey || event.metaKey; // metaKey is for Cmd key on Mac
				// Check if the Shift key is pressed
				const isShiftPressed = event.shiftKey;

				// Check if Ctrl + Shift + O is pressed
				if (isCtrlPressed && isShiftPressed && event.key.toLowerCase() === 'o') {
					event.preventDefault();
					console.log('newChat');
					document.getElementById('sidebar-new-chat-button')?.click();
				}

				// Check if Shift + Esc is pressed
				if (isShiftPressed && event.key === 'Escape') {
					event.preventDefault();
					console.log('focusInput');
					document.getElementById('chat-input')?.focus();
				}

				// Check if Ctrl + Shift + ; is pressed
				if (isCtrlPressed && isShiftPressed && event.key === ';') {
					event.preventDefault();
					console.log('copyLastCodeBlock');
					const button = [...document.getElementsByClassName('copy-code-button')]?.at(-1);
					button?.click();
				}

				// Check if Ctrl + Shift + C is pressed
				if (isCtrlPressed && isShiftPressed && event.key.toLowerCase() === 'c') {
					event.preventDefault();
					console.log('copyLastResponse');
					const button = [...document.getElementsByClassName('copy-response-button')]?.at(-1);
					console.log(button);
					button?.click();
				}

				// Check if Ctrl + Shift + S is pressed
				if (isCtrlPressed && isShiftPressed && event.key.toLowerCase() === 's') {
					event.preventDefault();
					console.log('toggleSidebar');
					document.getElementById('sidebar-toggle-button')?.click();
				}

				// Check if Ctrl + Shift + Backspace is pressed
				if (
					isCtrlPressed &&
					isShiftPressed &&
					(event.key === 'Backspace' || event.key === 'Delete')
				) {
					event.preventDefault();
					console.log('deleteChat');
					document.getElementById('delete-chat-button')?.click();
				}

				// Check if Ctrl + . is pressed
				if (isCtrlPressed && event.key === '.') {
					event.preventDefault();
					console.log('openSettings');
					showSettings.set(!$showSettings);
				}

				// Check if Ctrl + / is pressed
				if (isCtrlPressed && event.key === '/') {
					event.preventDefault();
					console.log('showShortcuts');
					document.getElementById('show-shortcuts-button')?.click();
				}

				// Check if Ctrl + Shift + ' is pressed
				if (isCtrlPressed && isShiftPressed && event.key.toLowerCase() === `'`) {
					event.preventDefault();
					console.log('temporaryChat');
					temporaryChatEnabled.set(!$temporaryChatEnabled);
					await goto('/');
					const newChatButton = document.getElementById('new-chat-button');
					setTimeout(() => {
						newChatButton?.click();
					}, 0);
				}
			});

			if ($page.url.searchParams.get('temporary-chat') === 'true') {
				temporaryChatEnabled.set(true);
			}

			await tick();
		}

		loaded = true;
	});
</script>

<SettingsModal bind:show={$showSettings} />

<div class="app relative">
	<div
		class="text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 h-screen max-h-[100dvh] overflow-auto flex flex-row"
	>
		{#if loaded}
			{#if !['user', 'admin'].includes($user.role)}
				<AccountPending />
			{/if}

			<div class="flex w-full">
				<Sidebar />
				<PaneGroup direction="horizontal" class="flex flex-1">
					<Pane minSize={20} defaultSize={$showDsp ? 40 : 100} class="flex-1">
						<div class="flex-1 min-w-0">
							<slot />
						</div>
					</Pane>
					{#if $showDsp}
						<PaneResizer class="relative flex w-2 items-center justify-center bg-background group">
							<div class="z-10 flex h-7 w-5 items-center justify-center rounded-sm">
								<EllipsisVertical className="size-4 invisible group-hover:visible" />
							</div>
						</PaneResizer>
						<Pane minSize={30} defaultSize={100} class="border-l dark:border-gray-800">
							<DspViewer />
						</Pane>
					{/if}
				</PaneGroup>
			</div>
		{/if}
	</div>
</div>

<style>
	.loading {
		display: inline-block;
		clip-path: inset(0 1ch 0 0);
		animation: l 1s steps(3) infinite;
		letter-spacing: -0.5px;
	}

	@keyframes l {
		to {
			clip-path: inset(0 -1ch 0 0);
		}
	}

	pre[class*='language-'] {
		position: relative;
		overflow: auto;

		/* make space  */
		margin: 5px 0;
		padding: 1.75rem 0 1.75rem 1rem;
		border-radius: 10px;
	}

	pre[class*='language-'] button {
		position: absolute;
		top: 5px;
		right: 5px;

		font-size: 0.9rem;
		padding: 0.15rem;
		background-color: #828282;

		border: ridge 1px #7b7b7c;
		border-radius: 5px;
		text-shadow: #c4c4c4 0 0 2px;
	}

	pre[class*='language-'] button:hover {
		cursor: pointer;
		background-color: #bcbabb;
	}
</style>
