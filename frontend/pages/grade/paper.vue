<template>
	<view class="container">
		<view class="card">
			<view class="label">选择试卷</view>
			<picker mode="selector" :range="paperLabels" :value="paperIndex" @change="onPaperChange">
				<view class="picker">{{ paperLabels[paperIndex] || '请先到"试卷库"上传试卷' }}</view>
			</picker>

			<view class="label" style="margin-top: 24rpx;">学生作答图片（正反面，最多 9 张）</view>
			<view class="img-grid">
				<view v-for="(p, i) in imagePaths" :key="i" class="thumb-wrap">
					<image :src="p" mode="aspectFill" class="thumb" />
					<view class="thumb-del" @click="removeImage(i)">×</view>
				</view>
				<view v-if="imagePaths.length < 9" class="thumb-add" @click="chooseImages">+</view>
			</view>

			<button class="btn-primary" :disabled="!canSubmit || loading" @click="submit" style="margin-top: 32rpx;">
				{{ loading ? 'AI 评分中...' : '提交整卷评分' }}
			</button>
		</view>

		<view v-if="loading" class="card muted">
			AI 正在识别整卷作答并对照打分，预计 30~90 秒，请耐心等待...
		</view>
	</view>
</template>

<script>
	import { getPaperList, gradePaper } from '@/api/index.js'
	export default {
		data() {
			return {
				papers: [],
				paperIndex: 0,
				imagePaths: [],
				loading: false
			}
		},
		computed: {
			paperLabels() {
				return this.papers.map(p => `${p.paper_name}（${p.question_count} 题）`)
			},
			canSubmit() {
				return this.papers.length > 0 && this.imagePaths.length > 0
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
				} catch (e) {
					uni.showToast({ title: e.message, icon: 'none' })
				}
			},
			onPaperChange(e) {
				this.paperIndex = e.detail.value
			},
			chooseImages() {
				const remain = 9 - this.imagePaths.length
				if (remain <= 0) return
				uni.chooseImage({
					count: remain,
					sizeType: ['compressed'],
					sourceType: ['album', 'camera'],
					success: (res) => {
						this.imagePaths = this.imagePaths.concat(res.tempFilePaths)
					}
				})
			},
			removeImage(i) {
				this.imagePaths.splice(i, 1)
			},
			async submit() {
				const paper = this.papers[this.paperIndex]
				if (!paper) return
				this.loading = true
				try {
					const r = await gradePaper(paper.paper_id, this.imagePaths)
					uni.setStorageSync('last_paper_grade_result', r.data)
					uni.navigateTo({ url: '/pages/grade/paper_result' })
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
	.picker {
		background: #F3F4F6;
		border-radius: 12rpx;
		padding: 20rpx 24rpx;
		font-size: 28rpx;
		color: #1F2937;
	}
	.img-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 16rpx;
	}
	.thumb-wrap {
		position: relative;
		width: 200rpx;
		height: 200rpx;
	}
	.thumb {
		width: 200rpx;
		height: 200rpx;
		border-radius: 12rpx;
		background: #F3F4F6;
	}
	.thumb-del {
		position: absolute;
		top: -10rpx;
		right: -10rpx;
		width: 40rpx;
		height: 40rpx;
		line-height: 36rpx;
		text-align: center;
		background: #DC2626;
		color: #fff;
		border-radius: 50%;
		font-size: 28rpx;
	}
	.thumb-add {
		width: 200rpx;
		height: 200rpx;
		border: 2rpx dashed #9CA3AF;
		border-radius: 12rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 60rpx;
		color: #9CA3AF;
		background: #F9FAFB;
	}
</style>
