<template>
	<rich-text class="math-text" :nodes="html"></rich-text>
</template>

<script>
	import katex from 'katex'

	const DELIMS = [
		{ open: '$$', close: '$$', display: true },
		{ open: '\\[', close: '\\]', display: true },
		{ open: '\\(', close: '\\)', display: false },
		{ open: '$', close: '$', display: false }
	]

	function escapeHtml(s) {
		return s
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#39;')
	}

	function findNext(text, from) {
		let best = null
		for (const d of DELIMS) {
			const idx = text.indexOf(d.open, from)
			if (idx === -1) continue
			if (!best || idx < best.idx) best = { idx, delim: d }
		}
		return best
	}

	function renderMath(src, displayMode) {
		try {
			return katex.renderToString(src, {
				displayMode,
				throwOnError: false,
				strict: 'ignore',
				output: 'html'
			})
		} catch (e) {
			return escapeHtml((displayMode ? '$$' : '$') + src + (displayMode ? '$$' : '$'))
		}
	}

	function renderText(src) {
		return escapeHtml(src).replace(/\n/g, '<br>')
	}

	function renderContent(raw) {
		if (raw === undefined || raw === null) return ''
		const text = String(raw)
		let out = ''
		let i = 0
		while (i < text.length) {
			const hit = findNext(text, i)
			if (!hit) {
				out += renderText(text.slice(i))
				break
			}
			if (hit.idx > i) out += renderText(text.slice(i, hit.idx))
			const start = hit.idx + hit.delim.open.length
			const end = text.indexOf(hit.delim.close, start)
			if (end === -1) {
				out += renderText(text.slice(hit.idx))
				break
			}
			const inner = text.slice(start, end)
			out += renderMath(inner, hit.delim.display)
			i = end + hit.delim.close.length
		}
		return out
	}

	export default {
		name: 'math-text',
		props: {
			content: { type: [String, Number], default: '' }
		},
		computed: {
			html() {
				return renderContent(this.content)
			}
		}
	}
</script>

<style>
	.math-text {
		font-size: 28rpx;
		color: #1F2937;
		line-height: 1.7;
		word-break: break-word;
	}
</style>
