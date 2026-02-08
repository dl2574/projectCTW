# Tech Stack Context

## Core Technologies
- **Django 6.0** - Python web framework
- **htmx** - HTML-driven AJAX interactions
- **Alpine.js 3.x** - Minimal JavaScript framework for client-side interactivity
- **Tailwind CSS 4.x** - Utility-first CSS framework
- **Standalone Tailwind CLI** (@tailwindcss/cli) - Build process via custom Django management commands

## Django 6.0 Key Features

### Template Partials (NEW in 6.0)
```html
{% partialdef user-info %}
    <div>{{ user.name }}</div>
{% endpartialdef %}

{% partial user-info %}
```
- Reference: `template.html#partial-name`
- Works with `{% include %}`, `render()`, `get_template()`

### Other Major Features
- **Tasks Framework** - Built-in background task system with `@task` decorator
- **CSP Support** - Content Security Policy via `ContentSecurityPolicyMiddleware`
- **Modern Email API** - Uses Python's `email.message.EmailMessage`
- **Async Pagination** - `AsyncPaginator` and `AsyncPage`

### Breaking Changes from 5.x
- **Requires Python 3.12+**
- `DEFAULT_AUTO_FIELD` now defaults to `BigAutoField`
- Default border/ring colors changed to `currentColor`
- ORM expressions must return params as tuples

## htmx Core Patterns

### Basic Syntax
```html
<button hx-post="/clicked"
        hx-trigger="click"
        hx-target="#parent-div"
        hx-swap="outerHTML">
    Click Me!
</button>
```

### Key Attributes
- **HTTP verbs**: `hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete`
- **Triggers**: `hx-trigger="keyup changed delay:500ms"`, `every 2s`, `revealed`, `load`
- **Targets**: `hx-target="closest tr"`, `next .item`, `find .result`
- **Swap**: `innerHTML`, `outerHTML`, `afterbegin`, `beforeend`, `delete`, `none`

### Request/Response Headers
- Request: `HX-Request: true`, `HX-Trigger`, `HX-Target`, `HX-Current-URL`
- Response: `HX-Trigger`, `HX-Redirect`, `HX-Refresh`, `HX-Retarget`

### Django Integration
```python
# Detect htmx requests
if request.headers.get('HX-Request'):
    return render(request, 'partial.html', context)
return render(request, 'full_page.html', context)
```

## Alpine.js Core Directives

### Component State
```html
<div x-data="{ count: 0, open: false }">
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
    <div x-show="open">Content</div>
</div>
```

### Essential Directives
- **x-data** - Component state
- **x-show** - Toggle visibility (CSS display)
- **x-if** - Conditional rendering (DOM removal, requires `<template>`)
- **x-for** - Loops (requires `<template>`)
- **x-on / @** - Event listeners (`@click`, `@submit.prevent`, `@click.away`)
- **x-model** - Two-way binding (`x-model.debounce.500ms`)
- **x-bind / :** - Bind attributes (`:disabled`, `:class="{ 'active': isActive }"`)
- **x-text** - Set text content
- **x-html** - Set HTML content
- **x-init** - Run on initialize
- **x-ref** - Reference elements
- **x-transition** - CSS transitions

### Magic Properties
- `$el` - Current element
- `$refs` - Access x-ref elements
- `$nextTick()` - Wait for DOM updates
- `$watch()` - Watch property changes
- `$store` - Global state
- `$dispatch()` - Custom events

## Tailwind CSS 4.x Changes

### Installation
```bash
npm install @tailwindcss/cli
npx @tailwindcss/cli -i input.css -o output.css
```

### CSS-First Configuration
```css
/* Old v3 */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* New v4 */
@import "tailwindcss";

@theme {
  --color-brand: #3b82f6;
  --font-display: "Inter", sans-serif;
  --spacing-18: 4.5rem;
  --breakpoint-3xl: 1920px;
}
```

### Major Breaking Changes
- **Browser Support**: Safari 16.4+, Chrome 111+, Firefox 128+
- **Renamed utilities**: `shadow` → `shadow-sm`, `ring` → `ring-3`, `rounded` → `rounded-sm`
- **Removed**: `bg-opacity-*` (use `bg-black/50` instead)
- **Default colors**: Border/ring now use `currentColor` instead of gray
- **Important modifier**: Now at end (`hover:bg-red-500!` not `hover:!bg-red-500`)
- **Variant order**: Left to right (CSS-like) not right to left
- **Transform transitions**: Must specify `transform,translate,scale,rotate`
- **No CSS preprocessors** (Sass/Less/Stylus not supported)

### New Features
- **Container Queries**: `@container`, `@sm:grid-cols-3`, `@max-md:grid-cols-1`
- **3D Transforms**: `rotate-x-45`, `scale-z-150`, `translate-z-12`
- **Dynamic utilities**: More flexible arbitrary values

### Custom Utilities
```css
/* Old v3 */
@layer utilities {
  .tab-4 { tab-size: 4; }
}

/* New v4 */
@utility tab-4 {
  tab-size: 4;
}
```

## Integration Patterns

### When to Use What
- **Alpine.js**: UI state (dropdowns, modals, tabs), client validation, animations, local filtering
- **htmx**: Server communication, loading content, form submissions, infinite scroll, polling
- **Django**: HTML rendering, business logic, database queries, authentication, template partials
- **Tailwind**: All styling, responsive design, hover states

### Common Pattern Example
```html
<!-- Alpine handles UI state, htmx handles server calls, Tailwind styles -->
<div x-data="{ expanded: false }" class="max-w-md mx-auto p-4">
  <button @click="expanded = !expanded"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    <span x-text="expanded ? 'Collapse' : 'Expand'"></span>
  </button>

  <div x-show="expanded"
       x-transition
       hx-get="/api/items"
       hx-trigger="revealed"
       hx-swap="innerHTML"
       class="mt-4">
    <!-- Content loaded by htmx -->
  </div>
</div>
```

### Form with Validation
```html
<div x-data="{ email: '', get isValid() { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email) } }">
  <form hx-post="/subscribe" hx-swap="outerHTML">
    <input x-model="email"
           :class="{ 'border-red-500': email && !isValid }"
           class="border rounded px-3 py-2">
    <button :disabled="!isValid"
            class="px-4 py-2 bg-green-500 text-white disabled:opacity-50">
      Subscribe
    </button>
  </form>
</div>
```

## Build Process
- Uses standalone Tailwind CLI via custom Django management commands
- No Vite or webpack
- Pure Django workflow with integrated frontend builds
