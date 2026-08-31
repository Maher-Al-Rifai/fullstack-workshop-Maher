<template>
  <div class="app-shell">
    <a href="#main-content" class="skip-link">Skip to main content</a>
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
/* Visually hidden until focused — gives keyboard users a path past the nav */
.skip-link {
  position: absolute;
  top: -100%;
  left: var(--space-4);
  z-index: 9999;
  padding: var(--space-2) var(--space-4);
  background: var(--color-brand);
  color: white;
  border-radius: 0 0 6px 6px;
  font-weight: 600;
  text-decoration: none;
}
.skip-link:focus {
  top: 0;
}
</style>
