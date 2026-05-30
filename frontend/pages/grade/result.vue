<template>
	<view class="container">
		<view v-if="!result" class="muted card">无评分结果</view>
		<view v-else>
			<view class="card score-card">
				<view class="score-big">
					<text class="score-num">{{ result.score_obtained }}</text>
					<text class="score-total"> / {{ result.full_score }}</text>
				</view>
				<view class="muted center">第 {{ result.matched_question.qno }} 题 · 得分</view>
			</view>

			<view class="card">
				<view class="section-title">题干</view>
				<math-text class="text-block" :content="result.matched_question.stem" />
			</view>

			<view class="card">
				<view class="section-title">学生作答（OCR 识别）</view>
				<math-text class="text-block" :content="result.student_answer_ocr || '（未识别到内容）'" />
			</view>

			<view class="card">
				<view class="section-title">标准答案</view>
				<math-text class="text-block" :content="result.matched_question.answer || '（试卷中未给出）'" />
				<view v-if="result.matched_question.explanation" style="margin-top: 16rpx;">
					<view class="section-title">参考解析</view>
					<math-text class="text-block" :content="result.matched_question.explanation" />
				</view>
			</view>

			<view class="card">
				<view class="section-title">扣分依据</view>
				<view v-if="result.deductions && result.deductions.length">
					<view v-for="(d, i) in result.deductions" :key="i" class="deduction-item">
						<text class="deduction-point">{{ d.point }}</text>
						<text class="deduction-num">-{{ d.deduct }}</text>
					</view>
				</view>
				<view v-else class="text-block">无明显扣分点</view>
			</view>

			<view class="card">
				<view class="section-title">AI 评语</view>
				<view class="text-block">{{ result.ai_comment || '（无）' }}</view>
			</view>

			<button class="btn-primary" @click="back" style="margin-top: 16rpx;">继续评下一题</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return { result: null }
		},
		onLoad() {
			this.result = uni.getStorageSync('last_grade_result') || null
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
	.section-title {
		font-size: 26rpx;
		color: #6B7280;
		margin-bottom: 12rpx;
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
		padding: 16rpx 0;
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
