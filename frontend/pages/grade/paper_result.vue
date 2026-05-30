<template>
	<view class="container">
		<view v-if="!result" class="muted card">无评分结果</view>
		<view v-else>
			<view class="card score-card">
				<view class="score-big">
					<text class="score-num">{{ result.total_score }}</text>
					<text class="score-total"> / {{ result.full_score }}</text>
				</view>
				<view class="muted center">{{ result.paper_name }} · 整卷得分</view>
			</view>

			<view v-for="(it, i) in result.items" :key="i" class="card item-card">
				<view class="item-head">
					<text class="qno">第 {{ it.qno }} 题</text>
					<text class="item-score">{{ it.score_obtained }} / {{ it.full_score }}</text>
				</view>

				<view v-if="!it.matched" class="warn">未在模型返回中匹配到该题，已记 0 分</view>

				<view class="section-title">题干</view>
				<math-text class="text-block" :content="(it.question && it.question.stem) || ''" />

				<view class="section-title">学生作答</view>
				<math-text class="text-block" :content="it.student_answer_ocr || '（未识别到内容）'" />

				<view class="section-title">标准答案</view>
				<math-text class="text-block" :content="(it.question && it.question.answer) || '（试卷中未给出）'" />

				<view v-if="it.question && it.question.explanation">
					<view class="section-title">参考解析</view>
					<math-text class="text-block" :content="it.question.explanation" />
				</view>

				<view class="section-title">扣分依据</view>
				<view v-if="it.deductions && it.deductions.length">
					<view v-for="(d, di) in it.deductions" :key="di" class="deduction-item">
						<text class="deduction-point">{{ d.point }}</text>
						<text class="deduction-num">-{{ d.deduct }}</text>
					</view>
				</view>
				<view v-else class="text-block">无明显扣分点</view>

				<view class="section-title">AI 评语</view>
				<view class="text-block">{{ it.ai_comment || '（无）' }}</view>
			</view>

			<button class="btn-primary" @click="back" style="margin-top: 16rpx;">返回</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return { result: null }
		},
		onLoad() {
			this.result = uni.getStorageSync('last_paper_grade_result') || null
		},
		methods: {
			back() {
				uni.navigateBack()
			}
		}
	}
</script>

<style>
	.score-card {
		text-align: center;
		padding: 40rpx 24rpx;
	}
	.score-big {
		font-size: 24rpx;
		color: #6B7280;
	}
	.score-num {
		font-size: 96rpx;
		font-weight: bold;
		color: #3B82F6;
	}
	.score-total {
		font-size: 36rpx;
		color: #6B7280;
	}
	.center {
		text-align: center;
	}
	.item-card {
		padding: 24rpx;
	}
	.item-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16rpx;
	}
	.qno {
		font-weight: 600;
		color: #3B82F6;
		font-size: 30rpx;
	}
	.item-score {
		color: #DC2626;
		font-weight: 600;
	}
	.warn {
		background: #FEF3C7;
		color: #92400E;
		padding: 12rpx 16rpx;
		border-radius: 12rpx;
		font-size: 26rpx;
		margin-bottom: 16rpx;
	}
	.section-title {
		font-size: 26rpx;
		color: #6B7280;
		margin: 16rpx 0 8rpx;
	}
	.text-block {
		font-size: 28rpx;
		color: #1F2937;
		line-height: 1.7;
		white-space: pre-wrap;
	}
	.deduction-item {
		display: flex;
		justify-content: space-between;
		padding: 12rpx 0;
		border-bottom: 1rpx solid #F3F4F6;
	}
	.deduction-item:last-child {
		border-bottom: none;
	}
	.deduction-point {
		flex: 1;
		font-size: 28rpx;
		color: #1F2937;
		padding-right: 20rpx;
	}
	.deduction-num {
		color: #DC2626;
		font-weight: 600;
	}
</style>
