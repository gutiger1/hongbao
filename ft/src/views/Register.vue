<template>
  <div class="register-container">
    <div class="carousel-container">
      <el-carousel interval="4000" height="80vh" :autoplay="true">
        <el-carousel-item v-for="(image, index) in carouselImages" :key="index">
          <img :src="image" alt="Carousel Image" class="carousel-image-full" />
        </el-carousel-item>
      </el-carousel>
    </div>
    <div class="register-box">
      <h2 class="register-title">注册</h2>
      <el-form :model="form" @submit.prevent="register" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="off" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input type="password" v-model="form.password" autocomplete="off" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" autocomplete="off" placeholder="请输入邮箱"></el-input>
          <el-button @click="sendCode" :disabled="codeSending" style="margin-top: 10px">发送验证码</el-button>
        </el-form-item>
        <el-form-item label="验证码">
          <el-input v-model="form.code" autocomplete="off" placeholder="请输入验证码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="register" class="register-button">注册</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/index.js';

const router = useRouter();
const route = useRoute();
const form = reactive({
  username: '',
  password: '',
  email: '',
  code: '',
  invite_code: ''  // 新增邀请码字段
});
const codeSending = ref(false);

const carouselImages = [
  `${apiClient.defaults.baseURL}/static/lunbotu/1.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/2.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/3.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/4.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/5.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/6.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/7.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/8.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/9.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/10.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/11.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/12.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/13.png`,
  `${apiClient.defaults.baseURL}/static/lunbotu/14.png`
];

onMounted(() => {
  // 从 URL 查询参数中获取邀请码
  const inviteCode = route.query.invite_code;
  if (inviteCode) {
    form.invite_code = inviteCode;  // 将邀请码赋值给表单
  }
});

const sendCode = async () => {
  if (!form.email) {
    ElMessage.error('请输入邮箱');
    return;
  }

  codeSending.value = true;
  try {
    await apiClient.post('/send-verification-code/', { email: form.email });
    ElMessage.success('验证码已发送');
  } catch (error) {
    ElMessage.error('发送验证码失败');
  } finally {
    codeSending.value = false;
  }
};

const register = async () => {
  try {
    const response = await apiClient.post('/register/', form, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    ElMessage.success('注册成功');
    router.push('/login');
  } catch (error) {
    if (error.response && error.response.data) {
      // 根据后端返回的错误信息做提示
      ElMessage.error(error.response.data.error || '注册失败');
    } else {
      ElMessage.error('注册失败');
    }
    console.error(error);
  }
};
</script>

<style scoped>
body,
html {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  /* 防止出现滚动条 */
}

.register-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  /* 确保全屏宽度 */
  height: 100vh;
  /* 确保全屏高度 */
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url('https://dingdanbaob.top/static/background-image.jpg');
  background-size: cover;
  /* 背景图覆盖整个容器 */
  background-position: center;
  /* 背景图居中 */
  background-repeat: no-repeat;
  /* 不重复 */
  box-sizing: border-box;
}

/* 轮播图容器 */
.carousel-container {
  width: 60%;
  /* 适当调整宽度 */
  height: 80vh;
  margin-right: 100px;
  box-sizing: border-box;
}

/* 轮播图图片 */
.carousel-image-full {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* 确保图片覆盖 */
}

/* 注册表单容器 */
.register-box {
  width: 400px;
  padding: 20px;
  background: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.register-title {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-input {
  width: 100%;
}

.register-button {
  width: 100%;
}
</style>
