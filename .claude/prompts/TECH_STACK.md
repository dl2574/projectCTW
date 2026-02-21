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

## ProjectCTW HTMX Patterns

These patterns are specific to features in this project. Use these as templates when building interactive UI.

### Django 6.0 Inline Partials (Preferred Approach)

Django 6.0 introduced `{% partialdef %}` to define reusable template fragments inline. This eliminates the need for separate partial files.

**Key Benefits:**
- Partials live in the same file as their parent template
- Easier to maintain - see full context in one place
- Can be rendered directly from views via `template.html#partial-name`

**Syntax - Define and Render Separately:**
```html
{% partialdef upvote-button %}
<button>▲ {{ event.number_of_upvotes }}</button>
{% endpartialdef %}

<!-- Render it elsewhere in template -->
{% partial upvote-button %}
```

**Syntax - Define and Render in One Place (use `inline`):**
```html
{% partialdef upvote-button inline %}
<button hx-post="{% url 'upvoteEvent' event.id %}"
        hx-target="this"
        hx-swap="outerHTML"
        class="{% if user_upvoted %}bg-green-500{% else %}bg-gray-200{% endif %}">
    ▲ {{ event.number_of_upvotes }}
</button>
{% endpartialdef %}
```

The `inline` keyword defines the partial AND renders it in place - no separate `{% partial %}` tag needed.

**Render from view (works with both approaches):**
```python
# Return just the partial, not the full template
return render(request, 'events/event_detail.html#upvote-button', context)
```

### When to Use What

| Approach | When to Use |
|----------|-------------|
| `{% partialdef name inline %}` | Define and render in one place (most common for HTMX) |
| `{% partialdef name %}` + `{% partial name %}` | Define once, render multiple times in same template |
| Separate file | Reused across multiple templates |

**Most event planning partials should use `inline`** since they're defined and rendered in one spot, but need to be targetable by HTMX responses.

### Pattern 1: Upvote Button (Toggle Action)

**Template: `events/event_detail.html`**
```html
{% partialdef upvote-button inline %}
<button hx-post="{% url 'upvoteEvent' event.id %}"
        hx-target="this"
        hx-swap="outerHTML"
        class="flex items-center gap-2 px-4 py-2 rounded
               {% if user_upvoted %}bg-green-500 text-white{% else %}bg-gray-200{% endif %}">
    <span>▲</span>
    <span>{{ event.number_of_upvotes }}</span>
</button>
{% endpartialdef %}
```

**View:**
```python
@login_required
def upvoteEvent(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.user_upvoted(request.user):
        event.upvotes.remove(request.user)
    else:
        event.upvotes.add(request.user)

    # Return just the partial using #fragment syntax
    return render(request, 'events/event_detail.html#upvote-button', {
        'event': event,
        'user_upvoted': event.user_upvoted(request.user)
    })
```

### Pattern 2: Date Voting (Render in Loop)

When rendering in a loop, define without `inline`, then use `{% partial %}` inside the loop:

**Template: `events/event_detail.html`**
```html
{% partialdef date-vote-item %}
<div id="date-{{ proposed_date.id }}" class="flex items-center justify-between p-3 border rounded">
    <span>{{ proposed_date.date|date:"M d, Y" }}</span>

    <div class="flex items-center gap-3">
        <span class="text-sm text-gray-600">{{ proposed_date.number_of_votes }} votes</span>

        <button hx-post="{% url 'voteDate' event.id proposed_date.id %}"
                hx-target="#date-{{ proposed_date.id }}"
                hx-swap="outerHTML"
                class="px-3 py-1 rounded
                       {% if user_voted %}bg-blue-500 text-white{% else %}bg-gray-200{% endif %}">
            {% if user_voted %}Voted{% else %}Vote{% endif %}
        </button>
    </div>
</div>
{% endpartialdef %}

<!-- Render in a loop (can't use inline here) -->
{% for proposed_date in plan.proposeddate_set.all %}
    {% partial date-vote-item %}
{% endfor %}
```

**View:**
```python
return render(request, 'events/event_detail.html#date-vote-item', {
    'event': event,
    'proposed_date': proposed_date,
    'user_voted': proposed_date.votes.filter(id=request.user.id).exists()
})
```

### Pattern 3: Add to List (Append New Items)

Similar to Pattern 2 - define without `inline` when rendering in a loop:

**Template: `events/event_detail.html`**
```html
{% partialdef supply-item %}
<div id="supply-{{ item.id }}" class="flex items-center justify-between p-3 border rounded">
    <div>
        <span class="font-medium">{{ item.name }}</span>
        <span class="text-sm text-gray-500">
            ({{ item.quantity_committed }}/{{ item.quantity_needed }}
            {% if item.is_fulfilled %}✓{% endif %})
        </span>
    </div>
    <!-- commitment form here (see Pattern 5) -->
</div>
{% endpartialdef %}

<!-- Form appends new items to the list -->
<form hx-post="{% url 'addSupply' event.id %}"
      hx-target="#supply-list"
      hx-swap="beforeend"
      hx-on::after-request="this.reset()">
    {% csrf_token %}
    <input type="text" name="item_name" placeholder="Item name" required>
    <input type="number" name="quantity" value="1" min="1">
    <button type="submit">Add Item</button>
</form>

<!-- Existing items rendered in loop -->
<div id="supply-list">
    {% for item in plan.supply_items.all %}
        {% partial supply-item %}
    {% endfor %}
</div>
```

**View returns just the new item partial:**
```python
@login_required
def addSupplyView(request, pk):
    event = get_object_or_404(Event, pk=pk)

    item, error = SupplyItem.add_item(
        plan=event.plan,
        name=request.POST.get('item_name'),
        quantity_needed=int(request.POST.get('quantity', 1)),
        category=request.POST.get('category', ''),
        added_by=request.user
    )

    if error:
        return HttpResponse(f'<div class="text-red-500">{error}</div>')

    # Use #fragment syntax to return just the partial
    return render(request, 'events/event_detail.html#supply-item', {
        'item': item,
        'event': event
    })
```

### Pattern 4: Attendance Toggle (Radio-like Buttons)

**Template: `events/event_detail.html`**
```html
{% partialdef attendance-buttons inline %}
<div id="attendance-buttons" class="flex gap-2">
    {% for status, label in statuses %}
        <button hx-post="{% url 'updateAttendance' event.id %}"
                hx-vals='{"status": "{{ status }}"}'
                hx-target="#attendance-buttons"
                hx-swap="outerHTML"
                class="px-4 py-2 rounded
                       {% if current_status == status %}
                           bg-blue-500 text-white
                       {% else %}
                           bg-gray-200 hover:bg-gray-300
                       {% endif %}">
            {{ label }}
        </button>
    {% endfor %}
</div>
{% endpartialdef %}
```

**View:**
```python
@login_required
def updateAttendanceView(request, pk):
    event = get_object_or_404(Event, pk=pk)
    status = request.POST.get('status')

    commitment, created = AttendanceCommitment.set_commitment(
        plan=event.plan,
        user=request.user,
        status=status
    )

    return render(request, 'events/event_detail.html#attendance-buttons', {
        'event': event,
        'current_status': status,
        'statuses': [
            ('YES', 'Attending'),
            ('MAYBE', 'Maybe'),
            ('NO', 'Not Attending')
        ]
    })
```

### Pattern 5: Supply Commitment (Inline Form)

Expanding on Pattern 3's `supply-item` partial with the commitment form:

**Template: `events/event_detail.html`**
```html
{% partialdef supply-item %}
<div id="supply-{{ item.id }}" class="flex items-center justify-between p-3 border rounded">
    <div>
        <span class="font-medium">{{ item.name }}</span>
        <span class="text-sm text-gray-500">
            ({{ item.quantity_committed }}/{{ item.quantity_needed }}
            {% if item.is_fulfilled %}✓{% endif %})
        </span>
    </div>

    <form hx-post="{% url 'commitSupply' event.id item.id %}"
          hx-target="#supply-{{ item.id }}"
          hx-swap="outerHTML"
          class="flex gap-2">
        {% csrf_token %}
        <input type="number" name="quantity" value="1" min="1"
               class="w-16 px-2 py-1 border rounded">
        <button type="submit" class="px-3 py-1 bg-green-500 text-white rounded">
            I'll bring this
        </button>
    </form>
</div>
{% endpartialdef %}
```

**View:**
```python
return render(request, 'events/event_detail.html#supply-item', {
    'item': item,
    'event': event
})
```

### Pattern 6: Delete with Confirmation (Alpine + HTMX)

```html
<div x-data="{ confirming: false }">
    <button x-show="!confirming"
            @click="confirming = true"
            class="text-red-500">
        Delete
    </button>

    <div x-show="confirming" class="flex gap-2">
        <span>Are you sure?</span>
        <button hx-delete="{% url 'deleteSupply' item.id %}"
                hx-target="#supply-{{ item.id }}"
                hx-swap="outerHTML"
                class="text-red-500">
            Yes
        </button>
        <button @click="confirming = false" class="text-gray-500">
            No
        </button>
    </div>
</div>
```

### Pattern 7: Loading States

```html
<button hx-post="{% url 'upvoteEvent' event.id %}"
        hx-target="this"
        hx-swap="outerHTML"
        hx-indicator="#spinner">
    <span class="htmx-indicator" id="spinner">Loading...</span>
    <span>Upvote</span>
</button>
```

Or use `hx-disabled-elt` to disable during request:
```html
<button hx-post="{% url 'addSupply' event.id %}"
        hx-disabled-elt="this">
    Add Item
</button>
```

### Pattern 8: Error Handling with HX-Trigger

**View returns error via header:**
```python
from django.http import HttpResponse

def addSupplyView(request, pk):
    item, error = SupplyItem.add_item(...)

    if error:
        response = HttpResponse(status=422)
        response['HX-Trigger'] = json.dumps({
            'showError': {'message': error}
        })
        return response

    return render(request, 'events/partials/supply_item.html', {'item': item})
```

**Listen for event in template:**
```html
<body hx-on:show-error="alert(event.detail.message)">
```

Or with Alpine for toast notifications:
```html
<div x-data="{ error: '' }"
     @show-error.window="error = $event.detail.message; setTimeout(() => error = '', 3000)">
    <div x-show="error" x-text="error" class="bg-red-500 text-white p-3 rounded"></div>
</div>
```

### HTMX + CSRF Token

CSRF is already configured in `base.html` via `hx-headers`. Verify this exists:
```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
```

This automatically includes CSRF token in all HTMX requests.

### Testing HTMX Endpoints

HTMX endpoints should work both ways:
- **With HTMX**: Return partial HTML
- **Without HTMX**: Redirect (fallback for non-JS)

```python
def upvoteEvent(request, pk):
    # ... logic ...

    if request.headers.get('HX-Request'):
        return render(request, 'events/partials/upvote_button.html', context)

    # Fallback for non-HTMX (direct URL access)
    return redirect('eventDetail', pk=pk)
```

## Build Process
- Uses standalone Tailwind CLI via custom Django management commands
- No Vite or webpack
- Pure Django workflow with integrated frontend builds
