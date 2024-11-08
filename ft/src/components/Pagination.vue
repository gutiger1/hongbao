<template>
    <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[10, 20, 30, 40]"
        layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" :prev-text="prevText" :next-text="nextText">
        <template #total>
            总数: {{ total }}
        </template>
        <template #jumper>
            去往 <el-input-number :modelValue="currentPage" :min="1" :max="pageCount" @change="handleCurrentChange" /> 页
        </template>
    </el-pagination>
</template>

<script>
export default {
    props: {
        currentPage: {
            type: Number,
            required: true
        },
        pageSize: {
            type: Number,
            required: true
        },
        total: {
            type: Number,
            required: true,
        },
        prevText: {
            type: String,
            default: "<"
        },
        nextText: {
            type: String,
            default: ">"
        },
        pageCount: {
            type: Number,
            required: true
        }
    },
    emits: ['update:currentPage', 'update:pageSize'],
    methods: {
        handleSizeChange(size) {
            this.$emit('update:pageSize', size);
        },
        handleCurrentChange(page) {
            this.$emit('update:currentPage', page);
        }
    }
};
</script>
