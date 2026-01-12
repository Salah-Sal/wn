import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

export function BackButton() {
  const navigate = useNavigate()

  return (
    <button
      onClick={() => navigate(-1)}
      className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] mb-4"
    >
      <ArrowLeft className="w-4 h-4" />
      Back
    </button>
  )
}
