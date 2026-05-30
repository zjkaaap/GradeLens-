<template>
	<view class="container">
		<view class="card">
			<view class="label">试卷名称</view>
			<input class="input" v-model="paperName" placeholder="例如：5月23日B卷" />

			<view class="label" style="margin-top: 24rpx;">选择 .docx 文件</view>
			<view class="file-row">
				<button class="btn-light" @click="chooseFile">选择文件</button>
				<text class="filename">{{ filename || '未选择' }}</text>
			</view>

			<button class="btn-primary" :disabled="!canSubmit || loading" @click="submit" style="margin-top: 32rpx;">
				{{ loading ? '上传解析中...' : '上传并解析' }}
			</button>
		</view>

		<view v-if="loading" class="card muted">正在调用后端解析，请稍候。试卷较长时可能需要 5-15 秒。</view>
	</view>
</template>

<script>
	import { uploadPaper } from '@/api/index.js'
	export default {
		data() {
			return {
				paperName: '',
				filePath: '',
				filename: '',
				loading: false
			}
		},
		computed: {
			canSubmit() {
				return this.paperName.trim() && this.filePath
			}
		},
		methods: {
			chooseFile() {
				// #ifdef H5
				uni.chooseFile({
					count: 1,
					extension: ['.docx'],
					success: (res) => {
						const f = res.tempFiles[0]
						this.filePath = res.tempFilePaths[0]
						this.filename = f.name || '已选择'
					}
				})
				// #endif
				// #ifdef APP-PLUS
				uni.chooseFile({
					count: 1,
					type: 'all',
					extension: ['.docx'],
					success: (res) => {
						const f = res.tempFiles[0]
						this.filePath = res.tempFilePaths[0]
						this.filename = f.name || '已选择'
					}
				})
				// #endif
			},
			async submit() {
				this.loading = true
				try {
					const r = await uploadPaper(this.filePath, this.paperName.trim())
					uni.showToast({
						title: `解析完成，共 ${r.data.question_count} 题`,
						icon: 'success',
						duration: 2000
					})
					setTimeout(() => {
						uni.switchTab({ url: '/pages/paper/list' })
					}, 1500)
				} catch (e) {
					uni.showModal({ title: '上传失败', content: e.message || '未知错误', showCancel: false })
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
	.input {
		background: #F3F4F6;
		border-radius: 12rpx;
		padding: 20rpx 24rpx;
		font-size: 28rpx;
	}
	.file-row {
		display: flex;
		align-items: center;
	}
	.btn-light {
		background: #E5EDFF;
		color: #3B82F6;
		font-size: 26rpx;
		border-radius: 12rpx;
		padding: 16rpx 24rpx;
		margin-right: 16rpx;
	}
	.filename {
		font-size: 26rpx;
		color: #6B7280;
	}
</style>
