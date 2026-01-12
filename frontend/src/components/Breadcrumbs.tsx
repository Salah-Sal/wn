import { Link, useLocation } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'

export function Breadcrumbs() {
  const location = useLocation()
  const pathParts = location.pathname.split('/').filter(Boolean)

  if (pathParts.length === 0) {
    return null
  }

  const breadcrumbs = pathParts.map((part, index) => {
    const path = '/' + pathParts.slice(0, index + 1).join('/')
    let label = decodeURIComponent(part)
    
    if (part === 'search') label = 'Search'
    else if (part === 'word') label = 'Word'
    else if (part === 'synset') label = 'Synset'
    else if (part === 'sense') label = 'Sense'
    
    return { path, label, isLast: index === pathParts.length - 1 }
  })

  return (
    <nav className="flex items-center gap-1 text-sm mb-4 overflow-x-auto">
      <Link
        to="/"
        className="flex items-center gap-1 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
      >
        <Home className="w-4 h-4" />
        <span>Home</span>
      </Link>
      {breadcrumbs.map((crumb) => (
        <span key={crumb.path} className="flex items-center gap-1">
          <ChevronRight className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          {crumb.isLast ? (
            <span className="text-[hsl(var(--foreground))] font-medium truncate max-w-48">
              {crumb.label}
            </span>
          ) : (
            <Link
              to={crumb.path}
              className="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] truncate max-w-48"
            >
              {crumb.label}
            </Link>
          )}
        </span>
      ))}
    </nav>
  )
}
