<script setup lang="ts">
// 不再需要RouterLink和HelloWorld
import zhCN from 'ant-design-vue/es/locale/zh_CN'
</script>

<template>
  <a-config-provider :locale="zhCN">
    <!-- <keep-alive> -->
      <router-view></router-view>
    <!-- </keep-alive> -->
  </a-config-provider>
</template>

<style>
/* 引入工业风格主题样式 */
@import './assets/industrial-theme.css';
</style>
