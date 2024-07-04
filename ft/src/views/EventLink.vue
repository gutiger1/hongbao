<template>
    <div>
        <el-button type="primary" @click="generateLink">生成活动链接</el-button>
        <div v-if="eventLink">
            <p>活动链接：<a :href="eventLink" target="_blank">{{ eventLink }}</a></p>
        </div>
    </div>
</template>
  
<script setup>
import { ref } from 'vue';
import apiClient from '@/api/index.js';

const eventLink = ref('');

const generateLink = async () => {
    try {
        const response = await apiClient.get('/generate-event-link/');
        eventLink.value = response.data.event_link;
    } catch (error) {
        console.error(error);
    }
};
</script>
