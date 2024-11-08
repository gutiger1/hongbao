<template>
  <div>
    <h1 class="maintitle">我的店铺</h1>
    <el-table :data="shops" style="width: 100%; margin-bottom: 20px;">
      <!-- 店铺名称列，包含修改图标 -->
      <el-table-column prop="name" label="店铺名称">
        <template v-slot="scope">
          <span>{{ scope.row.name }}</span>
          <!-- 修改按钮变为图标 -->
          <el-button type="text" size="mini" @click="openEditDialog(scope.row)">
            <el-icon>
              <Edit />
            </el-icon>
          </el-button>
        </template>
      </el-table-column>

      <el-table-column prop="second_level_users_count" label="用户数量"></el-table-column>
      <el-table-column prop="approved" label="审核状态" :formatter="formatApprovalStatus"></el-table-column>

      <!-- 订单来源 (店长) 列 -->
      <el-table-column label="订单来源">
        <template v-slot="scope">
          店长：{{ scope.row.tbnick || '未设置' }}
        </template>
      </el-table-column>

      <!-- 自动获取订单 -->
      <el-table-column label="自动获取订单">
        <template v-slot="scope">
          <el-button :type="scope.row.auto_fetch_enabled ? 'success' : 'primary'" @click="handleAutoFetch(scope.row)">
            {{ scope.row.auto_fetch_enabled ? '已开启' : '未开启' }}
          </el-button>
        </template>
      </el-table-column>

      <!-- 佣金设置，设置宽度为400px -->
      <el-table-column label="佣金设置" width="400">
        <template v-slot="scope">
          <div class="commission-settings">
            <!-- 佣金方式选择：一行显示三个选项 -->
            <el-radio-group v-model="scope.row.commission_method" class="commission-method-radio">
              <el-radio label="fixed">固定金额</el-radio>
              <el-radio label="percentage">比例佣金{{ scope.row.percentage_commission || 100 }}%</el-radio>
              <el-radio label="commission_and_principal">佣金+本金</el-radio>
            </el-radio-group>

            <!-- 佣金输入框和保存按钮在一行显示 -->
            <div class="commission-input-container">
              <el-input v-if="scope.row.commission_method === 'fixed'" v-model="scope.row.fixed_commission"
                placeholder="请输入固定佣金金额" class="commission-input"></el-input>
              <el-input v-if="scope.row.commission_method === 'percentage'" v-model="scope.row.percentage_commission"
                placeholder="请输入佣金百分比" class="commission-input" @input="updatePercentage(scope.row)"></el-input>
              <el-input v-if="scope.row.commission_method === 'commission_and_principal'"
                v-model="scope.row.fixed_commission_with_principal" placeholder="请输入佣金+本金的固定佣金"
                class="commission-input"></el-input>

              <!-- 保存按钮，位于右侧 -->
              <el-button @click="saveCommissionMethod(scope.row)" type="primary" size="small"
                class="save-btn">保存</el-button>
            </div>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增店铺弹窗 -->
    <el-button @click="dialogVisible = true" type="primary">新增店铺</el-button>
    <el-dialog v-model="dialogVisible" title="新增店铺" width="500px">
      <el-form :model="newShop" label-width="100px">
        <el-form-item label="店铺名称">
          <el-input v-model="newShop.name"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addShop">确定</el-button>
      </span>
    </el-dialog>

    <!-- 编辑店铺名称弹窗 -->
    <el-dialog v-model="editDialogVisible" title="修改店铺名称" width="500px">
      <el-form :model="editShop" label-width="100px">
        <el-form-item label="新店铺名称">
          <el-input v-model="editShop.name"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveShopName">保存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Edit } from '@element-plus/icons-vue'; // 引入图标组件
import apiClient from '../api/index.js';

const updatePercentage = (shop) => {
  if (!shop.percentage_commission || shop.percentage_commission === 0) {
    shop.percentage_commission = 100;
  }
};

const shops = ref([]);
const dialogVisible = ref(false);
const newShop = ref({ name: '', commission_method: 'percentage', percentage_commission: 100 });

const editDialogVisible = ref(false);
const editShop = ref({ id: '', name: '' });

const fetchShops = async () => {
  try {
    const response = await apiClient.get('shops/');
    shops.value = response.data;

    shops.value.forEach(shop => {
      if (!shop.commission_method) {
        shop.commission_method = 'percentage';
        shop.percentage_commission = 100;
      } else if (shop.commission_method === 'percentage' && (!shop.percentage_commission || shop.percentage_commission === 0)) {
        shop.percentage_commission = 100;
      }
    });
  } catch (error) {
    ElMessage.error('获取店铺信息失败');
    console.error('Failed to fetch shops:', error);
  }
};

const openEditDialog = (shop) => {
  editShop.value = { ...shop };
  editDialogVisible.value = true;
};

const saveShopName = async () => {
  try {
    const response = await apiClient.post(`/shops/${editShop.value.id}/update-name/`, {
      name: editShop.value.name,
    });
    if (response.data.success) {
      ElMessage.success('店铺名称修改成功');
      editDialogVisible.value = false;
      fetchShops();
    } else {
      ElMessage.error('修改失败');
    }
  } catch (error) {
    ElMessage.error('保存失败');
  }
};

const addShop = async () => {
  try {
    await apiClient.post('add-shop/', newShop.value);
    ElMessage.success('店铺新增成功');
    dialogVisible.value = false;
    fetchShops();
  } catch (error) {
    ElMessage.error('店铺新增失败');
    console.error('Failed to add shop:', error);
  }
};

const formatApprovalStatus = (row, column, cellValue) => {
  return cellValue ? '已审核(参与活动)' : '待审核(不参与活动)';
};

const saveCommissionMethod = async (shop) => {
  try {
    const response = await apiClient.post('/save-commission-method/', {
      shop_id: shop.id,
      commission_method: shop.commission_method,
      fixed_commission: shop.commission_method === 'fixed' ? shop.fixed_commission : null,
      percentage_commission: shop.commission_method === 'percentage' ? (shop.percentage_commission || 100) : null,
      fixed_commission_with_principal: shop.commission_method === 'commission_and_principal' ? shop.fixed_commission_with_principal : null,
    });

    if (response.data.status === 'success') {
      ElMessage.success('佣金设置保存成功');
    } else {
      ElMessage.error('保存失败');
    }
  } catch (error) {
    console.error('Failed to save commission method:', error);
    ElMessage.error('保存失败');
  }
};

const handleAutoFetch = (shop) => {
  // 检查店铺是否通过审核
  if (!shop.approved) {
    ElMessage.warning('店铺未审核，请联系管理员进行处理');
    return;
  }

  toggleAutoFetch(shop);
};

const toggleAutoFetch = async (shop) => {
  try {
    if (!shop.auto_fetch_enabled) {
      const response = await apiClient.post(`authorize-auto-fetch/`, { shop_id: shop.id });
      if (response.data.auth_url) {
        window.location.href = response.data.auth_url;
      }
    } else {
      ElMessageBox.confirm(
        '取消后再次开启将重新计费，时长不累计。确定要取消吗？',
        '确认取消授权',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
        .then(async () => {
          await apiClient.post('cancel-auto-fetch/', { shop_id: shop.id });
          ElMessage.success('已取消授权');
          fetchShops();
        })
        .catch(() => {
          ElMessage.info('操作已取消');
        });
    }
  } catch (error) {
    ElMessage.error('操作失败');
    console.error('Failed to toggle auto fetch:', error);
  }
};

onMounted(fetchShops);
</script>

<style scoped>
.commission-settings {
  display: flex;
  flex-direction: column;
}

.commission-method-radio {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.commission-input-container {
  display: flex;
  align-items: center;
}

.commission-input {
  flex: 1;
  margin-right: 10px;
}

.save-btn {
  margin-left: 10px;
}

.el-table__cell {
  white-space: normal !important;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding: 10px 0;
}
</style>
