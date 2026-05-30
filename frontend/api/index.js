// 后端服务地址；H5 调试用 localhost；APK 部署需替换为内网 IP（如 http://192.168.x.x:8000）
// 也可在 grade/upload 页提供输入框由用户自行配置并 uni.setStorageSync 持久化
const DEFAULT_BASE_URL = 'http://127.0.0.1:8000'

export function getBaseUrl() {
	const saved = uni.getStorageSync('BASE_URL')
	return saved || DEFAULT_BASE_URL
}

export function setBaseUrl(url) {
	uni.setStorageSync('BASE_URL', url)
}

function request(opts) {
	return new Promise((resolve, reject) => {
		uni.request({
			url: getBaseUrl() + opts.url,
			method: opts.method || 'GET',
			data: opts.data,
			header: opts.header || { 'Content-Type': 'application/json' },
			timeout: opts.timeout || 60000,
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data)
				} else {
					const msg = (res.data && res.data.detail) || `HTTP ${res.statusCode}`
					reject(new Error(msg))
				}
			},
			fail: (err) => reject(new Error(err.errMsg || '网络错误'))
		})
	})
}

export function uploadPaper(filePath, paperName) {
	return new Promise((resolve, reject) => {
		uni.uploadFile({
			url: getBaseUrl() + '/api/paper/upload',
			filePath,
			name: 'file',
			formData: { paper_name: paperName },
			timeout: 120000,
			success: (res) => {
				try {
					const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
					if (res.statusCode >= 200 && res.statusCode < 300) {
						resolve(data)
					} else {
						reject(new Error((data && data.detail) || `HTTP ${res.statusCode}`))
					}
				} catch (e) {
					reject(new Error('返回数据解析失败'))
				}
			},
			fail: (err) => reject(new Error(err.errMsg || '上传失败'))
		})
	})
}

export function getPaperList() {
	return request({ url: '/api/paper/list' })
}

export function getPaperDetail(id) {
	return request({ url: `/api/paper/${id}` })
}

export function deletePaper(id) {
	return request({ url: `/api/paper/${id}`, method: 'DELETE' })
}

export function gradeStudent(paperId, questionNo, stemKeyword, imagePath) {
	return new Promise((resolve, reject) => {
		uni.uploadFile({
			url: getBaseUrl() + '/api/grade',
			filePath: imagePath,
			name: 'image',
			formData: {
				paper_id: paperId,
				question_no: questionNo || '',
				stem_keyword: stemKeyword || ''
			},
			timeout: 180000,
			success: (res) => {
				try {
					const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
					if (res.statusCode >= 200 && res.statusCode < 300) {
						resolve(data)
					} else {
						reject(new Error((data && data.detail) || `HTTP ${res.statusCode}`))
					}
				} catch (e) {
					reject(new Error('返回数据解析失败'))
				}
			},
			fail: (err) => reject(new Error(err.errMsg || '评分请求失败'))
		})
	})
}

function readFileAsBase64(filePath) {
	return new Promise((resolve, reject) => {
		// #ifdef H5
		uni.request({
			url: filePath,
			method: 'GET',
			responseType: 'arraybuffer',
			success: (res) => {
				try {
					const bytes = new Uint8Array(res.data)
					let binary = ''
					for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i])
					resolve(btoa(binary))
				} catch (e) {
					reject(new Error('图片读取失败'))
				}
			},
			fail: (err) => reject(new Error(err.errMsg || '图片读取失败'))
		})
		return
		// #endif
		// #ifndef H5
		const fs = uni.getFileSystemManager()
		fs.readFile({
			filePath,
			encoding: 'base64',
			success: (res) => resolve(res.data),
			fail: (err) => reject(new Error(err.errMsg || '图片读取失败'))
		})
		// #endif
	})
}

export async function gradePaper(paperId, imagePaths) {
	const images_b64 = []
	for (const p of imagePaths) {
		images_b64.push(await readFileAsBase64(p))
	}
	return request({
		url: '/api/grade_paper',
		method: 'POST',
		data: { paper_id: paperId, images_b64 },
		timeout: 300000
	})
}
