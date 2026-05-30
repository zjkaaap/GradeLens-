<script>
	import 'katex/dist/katex.min.css'
	export default {
		onLaunch() {
			console.log('GradeLens 智阅 App Launch')
		}
	}
</script>

<style>
	page {
		background-color: #F5F7FA;
	}
	.container {
		padding: 24rpx;
	}
	.card {
		background: #fff;
		border-radius: 16rpx;
		padding: 24rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
	}
	.btn-primary {
		background: #3B82F6;
		color: #fff;
		border-radius: 12rpx;
		padding: 20rpx;
		font-size: 30rpx;
		text-align: center;
	}
	.btn-primary[disabled] {
		background: #9CB7E0;
	}
	.muted {
		color: #888;
		font-size: 26rpx;
	}
</style>
