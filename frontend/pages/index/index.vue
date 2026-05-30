<template>
	<view class="container">
		<view class="hero">
			<view class="hero-title">GradeLens 智阅</view>
			<view class="hero-sub">上传试卷 · 拍照作答 · AI 自动批改</view>
		</view>

		<view class="entry card" @click="go('/pages/paper/upload')">
			<view class="entry-icon">📄</view>
			<view class="entry-text">
				<view class="entry-title">上传试卷</view>
				<view class="entry-desc">导入完整试卷及解析 .docx 文件</view>
			</view>
		</view>

		<view class="entry card" @click="go('/pages/paper/list')">
			<view class="entry-icon">📚</view>
			<view class="entry-text">
				<view class="entry-title">试卷库</view>
				<view class="entry-desc">查看已上传试卷与题目</view>
			</view>
		</view>

		<view class="entry card" @click="go('/pages/grade/upload')">
			<view class="entry-icon">✏️</view>
			<view class="entry-text">
				<view class="entry-title">单题评分</view>
				<view class="entry-desc">按题号上传一张作答图片</view>
			</view>
		</view>

		<view class="entry card" @click="go('/pages/grade/paper')">
			<view class="entry-icon">📝</view>
			<view class="entry-text">
				<view class="entry-title">整卷评分</view>
				<view class="entry-desc">一次性上传正反面图片，AI 对照整卷打分</view>
			</view>
		</view>

		<view class="setting card" @click="editBaseUrl">
			<view class="muted">后端地址：{{ baseUrl }}</view>
			<view class="muted small">点此修改</view>
		</view>
	</view>
</template>

<script>
	import { getBaseUrl, setBaseUrl } from '@/api/index.js'
	export default {
		data() {
			return { baseUrl: '' }
		},
		onShow() {
			this.baseUrl = getBaseUrl()
		},
		methods: {
			go(path) {
				if (path.startsWith('/pages/paper/list') || path.startsWith('/pages/grade/upload')) {
					uni.switchTab({ url: path })
				} else {
					uni.navigateTo({ url: path })
				}
			},
			editBaseUrl() {
				const that = this
				uni.showModal({
					title: '修改后端地址',
					editable: true,
					placeholderText: 'http://192.168.x.x:8000',
					content: that.baseUrl,
					success: (r) => {
						if (r.confirm && r.content) {
							setBaseUrl(r.content.trim())
							that.baseUrl = r.content.trim()
							uni.showToast({ title: '已保存', icon: 'success' })
						}
					}
				})
			}
		}
	}
</script>

<style>
	.hero {
		padding: 60rpx 24rpx 30rpx;
		text-align: center;
	}
	.hero-title {
		font-size: 48rpx;
		font-weight: bold;
		color: #1F2937;
	}
	.hero-sub {
		margin-top: 12rpx;
		color: #6B7280;
		font-size: 26rpx;
	}
	.entry {
		display: flex;
		align-items: center;
		padding: 32rpx 24rpx;
	}
	.entry-icon {
		font-size: 56rpx;
		margin-right: 24rpx;
	}
	.entry-title {
		font-size: 32rpx;
		font-weight: 600;
		color: #1F2937;
	}
	.entry-desc {
		margin-top: 8rpx;
		font-size: 24rpx;
		color: #6B7280;
	}
	.setting {
		margin-top: 30rpx;
		text-align: center;
	}
	.small {
		font-size: 22rpx;
		color: #3B82F6;
		margin-top: 6rpx;
	}
</style>
