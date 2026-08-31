<script setup lang="ts">
const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/projects', label: 'Projects' },
]
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <NuxtLink to="/" class="brand" aria-label="Workboard home">
        Workboard
      </NuxtLink>
      <nav aria-label="Main navigation">
        <ul class="nav-list" role="list">
          <li v-for="link in links" :key="link.to">
            <NuxtLink :to="link.to" class="nav-link">{{ link.label }}</NuxtLink>
          </li>
        </ul>
      </nav>
      <div class="header-actions">
        <NuxtLink to="/login" class="btn btn-ghost">Sign in</NuxtLink>
        <NuxtLink to="/register" class="btn btn-primary">Register</NuxtLink>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: white;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: var(--content-width);
  margin: 0 auto;
  padding: 0 var(--space-4);
  height: 56px;
  display: flex;
  align-items: center;
  gap: var(--space-6);
}
.brand {
  font-weight: 700;
  font-size: 1.125rem;
  color: var(--color-brand);
  text-decoration: none;
  flex-shrink: 0;
}
.brand:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
  border-radius: 4px;
}
.nav-list {
  display: flex;
  gap: var(--space-1);
  list-style: none;
  margin: 0;
  padding: 0;
}
.nav-link {
  padding: 6px 12px;
  border-radius: 6px;
  text-decoration: none;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}
.nav-link:hover,
.nav-link.router-link-active {
  background: var(--color-surface);
  color: var(--color-text);
}
.nav-link:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
}
.header-actions {
  margin-left: auto;
  display: flex;
  gap: var(--space-2);
  align-items: center;
}
</style>
