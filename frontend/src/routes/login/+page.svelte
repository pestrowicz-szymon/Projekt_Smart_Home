<!-- src/routes/login/+page.svelte -->
<script>
  import { isAuthenticated, login } from './lib/stores/auth'
  import { goto } from '$app/navigation'
  import { onMount } from 'svelte'

  onMount(() => {
    if ($isAuthenticated) goto('/')
  })

  async function submit() {
    // ... fetch logic
    login(token)
    goto('/')
  }
</script>