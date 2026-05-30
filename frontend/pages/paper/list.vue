<template>
	<view class="container">
		<view v-if="loading" class="muted card">加载中...</view>
		<view v-else-if="papers.length === 0" class="empty card">
			<view>暂无试卷，请先上传</view>
			<button class="btn-primary" style="margin-top: 24rpx;" @click="goUpload">去上传</button>
		</view>
		<view v-else>
			<view v-for="p in papers" :key="p.paper_id" class="card paper-item" @click="goDetail(p.paper_id)">
				<view class="paper-name">{{ p.paper_name }}</view>
				<view class="muted">共 {{ p.question_count }} 题 · {{ formatTime(p.created_at) }}</view>
				<view class="actions">
					<button class="btn-mini" @click.stop="goGrade(p.paper_id)">评分</button>
					<button class="btn-mini btn-danger" @click.stop="confirmDelete(p)">删除</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import { getPaperList, deletePaper } from '@/api/index.js'
	export default {
		data() {
			return { papers: [], loading: false }
		},
		onShow() {
			this.load()
		},
		methods: {
			async load() {
				this.loading = true
				try {
					const r = await getPaperList()
					this.papers = r.data || []
				} catch (e) {
					uni.showToast({ title: e.message, icon: 'none' })
				} finally {
					this.loading = false
				}
			},
			formatTime(s) {
				if (!s) return ''
				return s.replace('T', ' ').slice(0, 19)
			},
			goUpload() {
				uni.navigateTo({ url: '/pages/paper/upload' })
			},
			goDetail(id) {
				uni.navigateTo({ url: `/pages/paper/detail?id=${id}` })
			},
			goGrade(id) {
				uni.setStorageSync('selected_paper_id', id)
				uni.switchTab({ url: '/pages/grade/upload' })
			},
			confirmDelete(p) {
				uni.showModal({
					title: '确认删除',
					content: `删除试卷"${p.paper_name}"？`,
					success: async (r) => {
						if (r.confirm) {
							try {
								await deletePaper(p.paper_id)
								this.load()
								uni.showToast({ title: '已删除', icon: 'success' })
							} catch (e) {
								uni.showToast({ title: e.message, icon: 'none' })
							}
						}
					}
				})
			}
		}
	}
</script>

<style>
	.empty {
		text-align: center;
		padding: 60rpx 24rpx;
		color: #6B7280;
	}
	.paper-name {
		font-size: 32rpx;
		font-weight: 600;
		color: #1F2937;
		margin-bottom: 10rpx;
	}
	.actions {
		margin-top: 16rpx;
		display: flex;
		gap: 16rpx;
	}
	.btn-mini {
		font-size: 24rpx;
		padding: 8rpx 24rpx;
		border-radius: 8rpx;
		background: #E5EDFF;
		color: #3B82F6;
		line-height: 1.6;
	}
	.btn-danger {
		background: #FEE2E2;
		color: #DC2626;
	}
</style>
