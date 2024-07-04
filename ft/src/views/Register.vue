<!-- <template>
  <el-form :model="form" @submit.native.prevent="register">
    <el-form-item label="用户名">
      <el-input v-model="form.username" autocomplete="off"></el-input>
    </el-form-item>
    <el-form-item label="密码">
      <el-input type="password" v-model="form.password" autocomplete="off"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="register">注册</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://192.168.158.138:8000/api/',
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json'
  }
});

export default {
  data() {
    return {
      form: {
        username: '',
        password: ''
      }
    };
  },
  methods: {
    register() {
      console.log("Sending data:", this.form);
      apiClient.post('register/', this.form)
        .then(response => {
          this.$message.success('注册成功');
          this.$router.push('/login');
        })
        .catch(error => {
          this.$message.error('注册失败');
          console.error(error);
        });
    }
  }
};
</script> -->

<template>
  <el-form :model="form" @submit.prevent="register">
    <el-form-item label="用户名">
      <el-input v-model="form.username" autocomplete="off"></el-input>
    </el-form-item>
    <el-form-item label="密码">
      <el-input type="password" v-model="form.password" autocomplete="off"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="register">注册</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const router = useRouter();
const form = reactive({
  username: '',
  password: ''
});

const register = async () => {
  try {
    console.log("Sending data:", form);
    const response = await axios.post('http://192.168.158.138:8000/api/register/', form, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    ElMessage.success('注册成功');
    router.push('/login');
  } catch (error) {
    ElMessage.error('注册失败');
    console.error(error);
  }
};
</script>
