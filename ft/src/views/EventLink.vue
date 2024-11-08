<template>
    <div>
        <h1 class="maintitle">活动管理</h1>
        <el-form :model="form" label-width="100px" class="form-container">
            <el-form-item label="活动标题">
                <el-input v-model="form.title" placeholder="请输入活动标题" class="short-input"></el-input>
            </el-form-item>
            <el-form-item label="广告说明图">
                <div class="image-upload-container">
                    <el-upload class="upload-demo" :http-request="uploadImage" list-type="picture-card"
                        :on-success="handleImageUpload" :file-list="fileList" :on-remove="handleImageRemove">
                        <div>
                            <i class="el-icon-plus upload-icon"></i>
                            <div class="el-upload__text">上传图片</div>
                        </div>
                    </el-upload>
                </div>
            </el-form-item>
            <el-form-item label="口令标题">
                <el-input v-model="form.commandTitle" placeholder="请输入口令标题" class="short-input"></el-input>
            </el-form-item>
            <el-form-item label="口令标题说明">
                <el-input v-model="form.commandDescription" placeholder="请输入口令标题说明" class="short-input"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="saveForm">保存</el-button>
            </el-form-item>
        </el-form>

        <!-- 展示活动链接和二维码 -->
        <el-form v-if="eventLink" label-width="100px" class="form-container">
            <el-form-item label="活动链接">
                <el-input v-model="eventLink" readonly class="short-input"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="copyLink">复制链接</el-button>
            </el-form-item>
            <el-form-item label="活动二维码">
                <canvas ref="qrcodeCanvas" class="qr-code-canvas"></canvas>
            </el-form-item>
            <el-form-item>
                <el-button type="success" @click="generateLink">重新生成活动链接</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api/index.js';
import QRCode from 'qrcode';
import { ElMessage } from 'element-plus';

const form = ref({
    id: null,
    title: '返佣活动',
    commandTitle: '口令',
    commandDescription: '请输入口令',
    image: ''
});
const eventLink = ref('');
const fileList = ref([]);
const qrcodeCanvas = ref(null);

const fetchEvent = async () => {
    try {
        const response = await apiClient.get('/fetch-event/');
        if (response.data) {
            form.value = response.data;
            if (form.value.image) {
                const fullUrl = `${apiClient.defaults.baseURL}${form.value.image}`;
                fileList.value = [{ name: form.value.image, url: fullUrl }];
            }
            if (form.value.id) {
                await generateLink();
            }
        }
    } catch (error) {
        console.error(error);
    }
};

const uploadImage = async ({ file, onSuccess, onError }) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
        const response = await apiClient.post('/upload-image/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        if (response.status === 200) {
            onSuccess(response.data, file);
            form.value.image = response.data.url;
            const fullUrl = `${apiClient.defaults.baseURL}${response.data.url}`;
            fileList.value = [{ name: file.name, url: fullUrl }];
        } else {
            onError(new Error('Upload failed'));
        }
    } catch (error) {
        console.error('Upload error:', error);
        onError(error);
    }
};

const handleImageUpload = (response, file) => {
    const fullUrl = `${apiClient.defaults.baseURL}${response.url}`;
    form.value.image = fullUrl;
    fileList.value = [{ name: file.name, url: fullUrl }];
};

const handleImageRemove = async (file) => {
    const imageUrl = form.value.image;
    form.value.image = '';
    try {
        await apiClient.post('/delete-image/', { url: imageUrl });
    } catch (error) {
        console.error('Failed to delete old image:', error);
    }
};

const saveForm = async () => {
    try {
        const response = await apiClient.post('/save-event/', form.value);
        form.value.id = response.data.id;
        ElMessage.success('保存成功');

        // 保存成功后立即生成活动链接和二维码
        await generateLink();
        await generateQRCode();
    } catch (error) {
        console.error(error);
        ElMessage.error('保存失败，请重试');
    }
};

const generateLink = async () => {
    try {
        const response = await apiClient.post('/generate-event-link/', { id: form.value.id });
        eventLink.value = response.data.event_link;
        await generateQRCode(eventLink.value);
    } catch (error) {
        console.error(error);
    }
};

const generateQRCode = async (url) => {
    if (qrcodeCanvas.value) {
        await QRCode.toCanvas(qrcodeCanvas.value, url, (error) => {
            if (error) console.error(error);
            console.log('QR code generated successfully!');
        });
    }
};

const copyLink = () => {
    navigator.clipboard.writeText(eventLink.value)
        .then(() => {
            ElMessage.success('链接已成功复制到剪贴板');
        })
        .catch((error) => {
            console.error('复制链接失败', error);
            ElMessage.error('复制失败，请手动复制链接');
        });
};

onMounted(() => {
    fetchEvent().then(() => {
        if (form.value.id) {
            generateLink();
        }
    });
});
</script>

<style scoped>
.form-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.short-input {
    width: 300px;
}

.upload-demo {
    display: inline-block;
    text-align: left;
}

.upload-icon {
    font-size: 28px;
    color: #8c939d;
}

.image-upload-container {
    display: flex;
    align-items: center;
}

.qr-code-canvas {
    width: 150px;
    height: 150px;
}

.el-upload .el-icon-plus {
    font-size: 28px;
    color: #8c939d;
}

.el-upload .el-upload__text {
    margin-top: 8px;
    font-size: 12px;
    color: #8c939d;
}
</style>
