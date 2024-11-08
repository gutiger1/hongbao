<template>
  <div>
    <!-- 全屏遮罩层，只有在 expiredDialogVisible 为 true 时显示 -->
    <div v-if="expiredDialogVisible" class="overlay"></div>
    <!-- 账户已到期的弹窗 -->
    <el-dialog v-model="expiredDialogVisible" title="账户已到期" width="500px" :close-on-click-modal="false"
      :close-on-press-escape="false" :show-close="false" class="custom-dialog">
      <div class="expired-dialog-content">
        <img :src="qrCodeUrl" alt="到期提醒二维码" class="dialog-image" />
        <p class="dialog-text">
          <span class="highlight-text">过期3天后将会删除账户信息</span>，请微信扫码联系客服续费。
        </p>
        <div class="center-content">
          <!-- 表单内容整体居中 -->
          <el-form :model="activationFormRenew" label-width="auto" class="custom-form">
            <el-form-item label="激活码" class="custom-form-item">
              <el-input v-model="activationFormRenew.code" placeholder="请输入续费激活码" class="custom-input" />
            </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="expiredDialogVisible = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="submitActivationCodeRenew" class="submit-btn">提交</el-button>
        </div>
      </template>
    </el-dialog>

    <h1 class="maintitle">总览/统计</h1>
    <el-row :gutter="20">
      <!-- 今日新增会员数量面板 -->
      <el-col :sm="12" :lg="6">
        <div class="small-panel user-reg suspension">
          <div class="small-panel-title">今日新增会员数量</div>
          <div class="small-panel-content">
            <div class="content-left">
              <el-icon>
                <Wallet />
              </el-icon>
              <span>{{ stats.new_members_today }}</span>
            </div>
            <div class="content-right">会员总数：{{ stats.total_members }}</div>
          </div>
        </div>
      </el-col>
      <!-- 今日总额面板 -->
      <el-col :sm="12" :lg="6">
        <div class="small-panel refunds suspension">
          <div class="small-panel-title">今日总额</div>
          <div class="small-panel-content">
            <div class="content-left">
              <el-icon>
                <Money />
              </el-icon>
              <span>{{ stats.total_refunds_today }}</span>
            </div>
            <div class="content-right">昨日总额：{{ stats.total_refunds_yesterday }}</div>
          </div>
        </div>
      </el-col>
      <!-- 未审核订单数量面板 -->
      <el-col :sm="12" :lg="6">
        <div class="small-panel pending-orders suspension">
          <div class="small-panel-title">未审核订单数量</div>
          <div class="small-panel-content">
            <div class="content-left">
              <Document />
              <span>{{ stats.pending_orders_count }}</span>
            </div>
            <div class="content-right">本月完成订单数：{{ stats.approved_orders_this_month }}</div>
          </div>
        </div>
      </el-col>
      <!-- 未分配店铺会员面板 -->
      <el-col :sm="12" :lg="6">
        <div class="small-panel unassigned-members suspension">
          <div class="small-panel-title">未分配店铺会员</div>
          <div class="small-panel-content">
            <div class="content-left">
              <User />
              <span>{{ stats.unassigned_members_count }}</span>
            </div>
            <div class="content-right">未分配会员占比：{{ stats.unassigned_members_percentage.toFixed(2) }}%</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 折线图和排行榜 -->
    <el-row :gutter="20" class="mt-4">
      <el-col :sm="18" :lg="18">
        <div class="chart-panel taller-panel">
          <div class="chart-title">
            <el-button-group>
              <el-button :type="chartType === 'monthly' ? 'primary' : 'default'" @click="switchToMonthly">月统计</el-button>
              <el-button :type="chartType === 'daily' ? 'primary' : 'default'" @click="switchToDaily">天统计</el-button>
            </el-button-group>
          </div>
          <div ref="refundChart" class="chart"></div>
        </div>
      </el-col>
      <el-col :sm="6" :lg="6">
        <div class="ranking-panel taller-panel">
          <div class="ranking-title">用户金额榜</div>
          <el-table :data="userRefundRanking" height="500" style="width: 100%">
            <el-table-column prop="username" label="用户名"></el-table-column>
            <el-table-column prop="total_refund" label="总额" width="100"></el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Wallet, Money, Document, User } from '@element-plus/icons-vue';
import apiClient from '@/api/index.js';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';

// 续费激活码表单
const activationFormRenew = ref({ code: '' });
const expiredDialogVisible = ref(false); // 控制过期弹窗的显示
const qrCodeUrl = ref(`${apiClient.defaults.baseURL}/static/erweima.png`); // 替代为示例图片的URL

const submitActivationCodeRenew = async () => {
  try {
    const response = await apiClient.post('/use-activation-code/', {
      code: activationFormRenew.value.code,
      action_type: 'renew',  // 续费操作
    });

    ElMessage({
      message: response.data.success || '续费成功！',
      type: 'success',
      duration: 3000,
      showClose: true,
    });

    expiredDialogVisible.value = false;
    activationFormRenew.value.code = ''; // 清空激活码
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '续费激活码使用失败');
  }
};

// 检查账户状态是否过期
const checkAccountStatus = async () => {
  try {
    const response = await apiClient.get('/user-info/');
    const { is_expired } = response.data;

    if (is_expired) {
      expiredDialogVisible.value = true; // 显示过期弹窗
    }
  } catch (error) {
    console.error('Failed to check account status:', error);
  }
};

// Mock 数据
const stats = ref({
  new_members_today: 0,
  total_refunds_today: 0,
  total_refunds_yesterday: 0,
  pending_orders_count: 0,
  approved_orders_this_month: 0,
  unassigned_members_count: 0,
  unassigned_members_percentage: 0,
  total_members: 0,
});

// 加载统计数据
const fetchStats = async () => {
  try {
    const response = await apiClient.get('/dashboard-stats/');
    stats.value = response.data;
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error);
  }
};

const userRefundRanking = ref([]);
const chartType = ref('monthly'); // 默认统计类型为月统计

const fetchRefunds = async () => {
  try {
    let response;
    if (chartType.value === 'monthly') {
      response = await apiClient.get('/monthly-refunds/');
    } else {
      response = await apiClient.get('/daily-refunds/');
    }
    renderRefundChart(response.data, chartType.value);
  } catch (error) {
    console.error('Failed to fetch refunds:', error);
  }
};

const fetchUserRefundRanking = async () => {
  try {
    const response = await apiClient.get('/user-refund-ranking/');
    userRefundRanking.value = response.data;
  } catch (error) {
    console.error('Failed to fetch user refund ranking:', error);
  }
};

const renderRefundChart = (data, type) => {
  const chartDom = document.querySelector('.chart');
  if (!chartDom) {
    console.error('Canvas element is null');
    return;
  }
  const myChart = echarts.init(chartDom);

  const reversedXAxis = (type === 'monthly' ? data.months : data.days).slice().reverse();
  const reversedSeriesData = Object.keys(data.data).map(shop => ({
    name: shop,
    type: 'line',
    data: data.data[shop].slice().reverse(),
  }));

  const option = {
    title: {
      text: type === 'monthly' ? '每月总返款额' : '每天返款额（30天）',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: Object.keys(data.data),
      bottom: 40,
    },
    grid: {
      top: 60,
      left: '3%',
      right: '4%',
      bottom: 90,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: reversedXAxis,
    },
    yAxis: {
      type: 'value',
    },
    series: reversedSeriesData,
  };
  myChart.setOption(option);
};

const switchToMonthly = () => {
  chartType.value = 'monthly';
  fetchRefunds();
};

const switchToDaily = () => {
  chartType.value = 'daily';
  fetchRefunds();
};

onMounted(() => {
  fetchStats();
  fetchRefunds();
  fetchUserRefundRanking();
  checkAccountStatus(); // 检查是否过期并显示弹窗
});
</script>

<style scoped>
.small-panel {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.small-panel-title {
  font-size: 16px;
  margin-bottom: 10px;
}

.small-panel-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-left {
  display: flex;
  align-items: center;
}

.content-left span {
  font-size: 24px;
  font-weight: bold;
  margin-left: 10px;
}

.chart-panel,
.ranking-panel {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-top: 20px;
}

.taller-panel {
  height: 600px;
}

.chart-title,
.ranking-title {
  font-size: 16px;
  margin-bottom: 10px;
}

.chart {
  width: 100%;
  height: 100%;
}

.mt-4 {
  margin-top: 20px;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  z-index: 2001;
}

.dialog-image {
  display: block;
  margin: 0 auto 20px;
  width: 200px;
  height: 200px;
  object-fit: contain;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding: 10px 0;

  .el-button {
    margin-left: 10px;
  }
}

.dialog-text {
  text-align: center;
  font-size: 16px;
  color: #333;
  margin-bottom: 20px;
  line-height: 1.8;
}

.highlight-text {
  font-weight: bold;
  color: #e74c3c;
  /* 高亮部分为红色 */
}

.custom-input .el-input__inner {
  border-radius: 8px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  font-size: 14px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  /* 输入框阴影 */
}

.custom-form-item {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.custom-form-item label {
  margin-right: 10px;
  /* 增加标签和输入框之间的间距 */
}

.center-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
