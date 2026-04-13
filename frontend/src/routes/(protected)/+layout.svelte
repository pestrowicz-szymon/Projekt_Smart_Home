<script>
  import { isAuthenticated } from '$lib/stores/auth'
  import { goto } from '$app/navigation'
  import { onMount } from 'svelte'

  onMount(() => {
    if (!$isAuthenticated) goto('/login')
  })
</script>

<slot />