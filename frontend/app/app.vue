<template>
  <div class="app-shell">
    <AppHeader />
    <main id="main-content" class="page-content">
      <NuxtPage />
    </main>
    <AppFooter />
  </div>
</template>

<style>
.app-shell {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
}
.page-content {
  flex: 1;
  width: min(var(--content-width), 100% - 2 * var(--space-4));
  margin: 0 auto;
  padding: var(--space-8) 0;
}
</style>
