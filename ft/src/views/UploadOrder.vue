<template>
    <el-form ref="form" label-width="120px">
        <el-form-item label="上传订单表格">
            <el-upload :action="null" :before-upload="handleBeforeUpload" :auto-upload="false" :file-list="fileList"
                accept=".csv, .xls, .xlsx">
                <el-button type="primary">选取文件</el-button>
            </el-upload>
            <a :href="sampleFileUrl" download>下载示例文件</a> <!-- 示例文件下载链接 -->
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm">上传</el-button>
        </el-form-item>
        <br>
        <img src="http://192.168.158.138:8000/static/sample.png" class="samplepic">
    </el-form>
</template>
  
<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '../api/index.js';

const fileList = ref([]);
const selectedFile = ref(null);
const sampleFileUrl = ref('http://192.168.158.138:8000/static/sample_order.xlsx'); // 示例文件URL

const handleBeforeUpload = (file) => {
    console.log('handleBeforeUpload called with file:', file);
    fileList.value = [file];
    selectedFile.value = file;
    return false; // 阻止自动上传
};

const submitForm = async () => {
    console.log('File list before upload:', fileList.value);
    if (!selectedFile.value) {
        ElMessage.error('请选择文件');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile.value);

    console.log('Uploading file:', selectedFile.value);

    try {
        const response = await apiClient.post('upload-order/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        if (response.data.failed_orders) {
            ElMessage.warning(`部分订单上传成功，但以下订单失败: ${response.data.failed_orders.join(', ')}`);
        } else {
            ElMessage.success('订单上传成功');
        }
        fileList.value = [];
        selectedFile.value = null;
    } catch (error) {
        console.error('Upload error:', error);
        ElMessage.error(error.response.data.error || '订单上传失败');
    }
};
</script>
  
<style scoped>
.samplepic {
    margin-top: 60px;
    width: 600px;
}
</style>