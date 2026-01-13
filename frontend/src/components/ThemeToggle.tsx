import { Sun, Moon, Monitor } from 'lucide-react'
import { useThemeStore } from '@/stores/themeStore'

export function ThemeToggle() {
  const { theme, setTheme } = useThemeStore()

  const cycleTheme = () => {
    const themes: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system']
    const currentIndex = themes.indexOf(theme)
    const nextIndex = (currentIndex + 1) % themes.length
    setTheme(themes[nextIndex])
  }

  return (
    <button
      onClick={cycleTheme}
      className="p-2 rounded-lg hover:bg-[hsl(var(--secondary))] transition-colors"
      title={`Theme: ${theme}`}
    >
      {theme === 'light' && <Sun className="w-5 h-5 text-[hsl(var(--foreground))]" />}
      {theme === 'dark' && <Moon className="w-5 h-5 text-[hsl(var(--foreground))]" />}
      {theme === 'system' && <Monitor className="w-5 h-5 text-[hsl(var(--foreground))]" />}
    </button>
  )
}
