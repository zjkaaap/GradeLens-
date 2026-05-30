<template>
	<view class="container">
		<view v-if="loading" class="card muted">加载中...</view>
		<view v-else-if="paper">
			<view class="card paper-head">
				<view class="title">{{ paper.paper_name }}</view>
				<view class="muted">共 {{ paper.questions.length }} 题</view>
			</view>
			<view v-for="q in paper.questions" :key="q.id" class="card q-card">
				<view class="q-head">
					<text class="q-no">第 {{ q.qno }} 题</text>
					<text class="q-score">{{ q.score }} 分</text>
				</view>
				<math-text class="q-stem" :content="q.stem" />
				<view class="q-toggle" @click="toggle(q.id)">
					{{ expanded[q.id] ? '收起答案与解析' : '展开标准答案与解析' }}
				</view>
				<view v-if="expanded[q.id]" class="q-answer">
					<view class="answer-label">标准答案：</view>
					<math-text class="answer-text" :content="q.answer || '（试卷中未给出）'" />
					<view v-if="q.explanation" class="answer-label" style="margin-top: 16rpx;">参考解析：</view>
					<math-text v-if="q.explanation" class="answer-text" :content="q.explanation" />
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import { getPaperDetail } from '@/api/index.js'
	export default {
		data() {
			return { paper: null, loading: true, expanded: {} }
		},
		onLoad(query) {
			this.id = query.id
			this.load()
		},
		methods: {
			async load() {
				try {
					const r = await getPaperDetail(this.id)
					this.paper = r.data
				} catch (e) {
					uni.showToast({ title: e.message, icon: 'none' })
				} finally {
					this.loading = false
				}
			},
			toggle(qid) {
				this.expanded = { ...this.expanded, [qid]: !this.expanded[qid] }
			}
		}
	}
</script>

<style>
	.title {
		font-size: 36rpx;
		font-weight: bold;
		color: #1F2937;
	}
	.q-head {
		display: flex;
		justify-content: space-between;
		margin-bottom: 12rpx;
	}
	.q-no {
		font-weight: 600;
		color: #3B82F6;
	}
	.q-score {
		color: #DC2626;
		font-size: 26rpx;
	}
	.q-stem {
		font-size: 28rpx;
		color: #1F2937;
		white-space: pre-wrap;
		line-height: 1.6;
	}
	.q-toggle {
		margin-top: 16rpx;
		color: #3B82F6;
		font-size: 26rpx;
	}
	.q-answer {
		margin-top: 16rpx;
		background: #F9FAFB;
		border-radius: 12rpx;
		padding: 16rpx;
	}
	.answer-label {
		font-size: 26rpx;
		color: #6B7280;
		margin-bottom: 6rpx;
	}
	.answer-text {
		font-size: 28rpx;
		color: #1F2937;
		white-space: pre-wrap;
		line-height: 1.6;
	}
</style>
