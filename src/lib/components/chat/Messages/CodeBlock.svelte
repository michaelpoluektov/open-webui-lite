<script lang="ts">
	import hljs from 'highlight.js';
	import mermaid from 'mermaid';

	import { v4 as uuidv4 } from 'uuid';

	import { copyToClipboard } from '$lib/utils';
	import { createEventDispatcher, getContext, onMount } from 'svelte';

	import 'highlight.js/styles/github-dark.min.css';

	import CodeEditor from '$lib/components/common/CodeEditor.svelte';
	import SvgPanZoom from '$lib/components/common/SVGPanZoom.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let id = '';

	export let save = false;

	export let token;
	export let lang = '';
	export let code = '';

	export let className = 'my-2';
	export let editorClassName = '';
	export let stickyButtonsClassName = 'top-8';

	let _code = '';
	$: if (code) {
		updateCode();
	}

	const updateCode = () => {
		_code = code;
	};

	let _token = null;

	let mermaidHtml = null;

	let executing = false;

	let stdout = null;
	let stderr = null;
	let result = null;

	let copied = false;
	let saved = false;

	const saveCode = () => {
		saved = true;

		code = _code;
		dispatch('save', code);

		setTimeout(() => {
			saved = false;
		}, 1000);
	};

	const copyCode = async () => {
		copied = true;
		await copyToClipboard(code);

		setTimeout(() => {
			copied = false;
		}, 1000);
	};

	const drawMermaidDiagram = async () => {
		try {
			if (await mermaid.parse(code)) {
				const { svg } = await mermaid.render(`mermaid-${uuidv4()}`, code);
				mermaidHtml = svg;
			}
		} catch (error) {
			console.log('Error:', error);
		}
	};

	const render = async () => {
		if (lang === 'mermaid' && (token?.raw ?? '').slice(-4).includes('```')) {
			(async () => {
				await drawMermaidDiagram();
			})();
		}
	};

	$: if (token) {
		if (JSON.stringify(token) !== JSON.stringify(_token)) {
			_token = token;
		}
	}

	$: if (_token) {
		render();
	}

	$: dispatch('code', { lang, code });

	onMount(async () => {
		console.log('codeblock', lang, code);

		if (lang) {
			dispatch('code', { lang, code });
		}
		if (document.documentElement.classList.contains('dark')) {
			mermaid.initialize({
				startOnLoad: true,
				theme: 'dark',
				securityLevel: 'loose'
			});
		} else {
			mermaid.initialize({
				startOnLoad: true,
				theme: 'default',
				securityLevel: 'loose'
			});
		}
	});
</script>

<div>
	<div class="relative {className} flex flex-col rounded-lg" dir="ltr">
		{#if lang === 'mermaid'}
			{#if mermaidHtml}
				<SvgPanZoom
					className=" border border-gray-50 dark:border-gray-850 rounded-lg max-h-fit overflow-hidden"
					svg={mermaidHtml}
					content={_token.text}
				/>
			{:else}
				<pre class="mermaid">{code}</pre>
			{/if}
		{:else}
			<div class="text-text-300 absolute pl-4 py-1.5 text-xs font-medium dark:text-white">
				{lang}
			</div>

			<div
				class="sticky {stickyButtonsClassName} mb-1 py-1 pr-2.5 flex items-center justify-end z-10 text-xs text-black dark:text-white"
			>
				<div class="flex items-center gap-0.5 translate-y-[1px]">
					{#if save}
						<button
							class="save-code-button bg-none border-none bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md px-1.5 py-0.5"
							on:click={saveCode}
						>
							{saved ? $i18n.t('Saved') : $i18n.t('Save')}
						</button>
					{/if}

					<button
						class="copy-code-button bg-none border-none bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md px-1.5 py-0.5"
						on:click={copyCode}>{copied ? $i18n.t('Copied') : $i18n.t('Copy')}</button
					>
				</div>
			</div>

			<div
				class="language-{lang} rounded-t-lg -mt-8 {editorClassName
					? editorClassName
					: executing || stdout || stderr || result
						? ''
						: 'rounded-b-lg'} overflow-hidden"
			>
				<div class=" pt-7 bg-gray-50 dark:bg-gray-850"></div>
				<CodeEditor
					value={code}
					{id}
					{lang}
					on:save={() => {
						saveCode();
					}}
					on:change={(e) => {
						_code = e.detail.value;
					}}
				/>
			</div>

			<div
				id="plt-canvas-{id}"
				class="bg-[#202123] text-white max-w-full overflow-x-auto scrollbar-hidden"
			/>

			{#if executing}
				<div class="bg-[#202123] text-white px-4 py-4 rounded-b-lg">
					<div class=" text-gray-500 text-xs mb-1">STDOUT/STDERR</div>
					<div class="text-sm">Running...</div>
				</div>
			{:else if stdout || stderr || result}
				<div class="bg-[#202123] text-white px-4 py-4 rounded-b-lg">
					<div class=" text-gray-500 text-xs mb-1">STDOUT/STDERR</div>
					<div class="text-sm">{stdout || stderr || result}</div>
				</div>
			{/if}
		{/if}
	</div>
</div>
