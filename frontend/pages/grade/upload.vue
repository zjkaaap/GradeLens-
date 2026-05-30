<template>
	<view class="container">
		<view class="card">
			<view class="label">选择试卷</view>
			<picker mode="selector" :range="paperLabels" :value="paperIndex" @change="onPaperChange">
				<view class="picker">{{ paperLabels[paperIndex] || '请先到"试卷库"上传试卷' }}</view>
			</picker>

			<view class="label" style="margin-top: 24rpx;">题号（必填，与试卷中一致）</view>
			<input class="input" v-model="questionNo" placeholder="例如：3" />

			<view class="label" style="margin-top: 24rpx;">题干关键字（题号无法对上时使用）</view>
			<input class="input" v-model="stemKeyword" placeholder="可留空" />

			<view class="label" style="margin-top: 24rpx;">学生作答图片</view>
			<view class="img-row">
				<view v-if="imagePath" class="img-thumb">
					<image :src="imagePath" mode="aspectFit" class="thumb" />
				</view>
				<button class="btn-light" @click="chooseImage">{{ imagePath ? '重新选择' : '选择图片' }}</button>
			</view>

			<button class="btn-primary" :disabled="!canSubmit || loading" @click="submit" style="margin-top: 32rpx;">
				{{ loading ? 'AI 评分中...' : '提交评分' }}
			</button>
		</view>

		<view v-if="loading" class="card muted">
			AI 正在识别图片并评分，预计需要 10-30 秒，请耐心等待...
		</view>
	</view>
</template>

<script>
	import { getPaperList, gradeStudent } from '@/api/index.js'
	export default {
		data() {
			return {
				papers: [],
				paperIndex: 0,
				questionNo: '',
				stemKeyword: '',
				imagePath: '',
				loading: false
			}
		},
		computed: {
			paperLabels() {
				return this.papers.map(p => `${p.paper_name}（${p.question_count} 题）`)
			},
			canSubmit() {
				return this.papers.length > 0 && this.imagePath && (this.questionNo || this.stemKeyword)
			}
		},
		onShow() {
			this.loadPapers()
		},
		methods: {
			async loadPapers() {
				try {
					const r = await getPaperList()
					this.papers = r.data || []
					const preselected = uni.getStorageSync('selected_paper_id')
					if (preselected) {
						const idx = this.papers.findIndex(p => p.paper_id === preselected)
						if (idx >= 0) this.paperIndex = idx
						uni.removeStorageSync('selected_paper_id')
					}
				} catch (e) {
					uni.showToast({ title: e.message, icon: 'none' })
				}
			},
			onPaperChange(e) {
				this.paperIndex = e.detail.value
			},
			chooseImage() {
				uni.chooseImage({
					count: 1,
					sizeType: ['compressed'],
					sourceType: ['album', 'camera'],
					success: (res) => {
						this.imagePath = res.tempFilePaths[0]
					}
				})
			},
			async submit() {
				const paper = this.papers[this.paperIndex]
				if (!paper) return
				this.loading = true
				try {
					const r = await gradeStudent(
						paper.paper_id,
						this.questionNo.trim(),
						this.stemKeyword.trim(),
						this.imagePath
					)
					uni.setStorageSync('last_grade_result', r.data)
					uni.navigateTo({ url: '/pages/grade/result' })
				} catch (e) {
					uni.showModal({ title: '评分失败', content: e.message || '未知错误', showCancel: false })
				} finally {
					this.loading = false
				}
			}
		}
	}
</script>

<style>
	.label {
		font-size: 28rpx;
		color: #374151;
		margin-bottom: 12rpx;
	}
	.input, .picker {
		background: #F3F4F6;
		border-radius: 12rpx;
		padding: 20rpx 24rpx;
		font-size: 28rpx;
		color: #1F2937;
	}
	.img-row {
		display: flex;
		flex-direction: column;
		gap: 16rpx;
	}
	.thumb {
		width: 100%;
		max-height: 400rpx;
		border-radius: 12rpx;
		background: #F3F4F6;
	}
	.btn-light {
		background: #E5EDFF;
		color: #3B82F6;
		font-size: 26rpx;
		border-radius: 12rpx;
		padding: 16rpx 24rpx;
		align-self: flex-start;
	}
</style>
