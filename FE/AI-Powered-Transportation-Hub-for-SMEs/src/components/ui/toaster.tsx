// components/ui/toaster.tsx
import { useToast } from "./use-toast"
import { X, CheckCircle, AlertCircle, Info } from "lucide-react"

export function Toaster() {
  const { toasts, dismiss } = useToast()

  return (
    <div className="fixed top-0 right-0 z-[100] flex flex-col p-4 gap-2 w-full max-w-sm">
      {toasts.map(function ({ id, title, description, variant }) {
        // Chọn màu sắc và icon dựa trên variant
        let bgClass = "bg-white dark:bg-gray-800 border-gray-200"
        let icon = <Info className="w-5 h-5 text-blue-500" />
        
        if (variant === "destructive") {
          bgClass = "bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800"
          icon = <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
        } else if (variant === "success") {
          bgClass = "bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800"
          icon = <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
        }

        return (
          <div
            key={id}
            className={`
              ${bgClass}
              relative flex items-start gap-3 p-4 rounded-lg border shadow-lg 
              transition-all duration-300 animate-in slide-in-from-right-full
            `}
          >
            <div className="flex-shrink-0 mt-0.5">
              {icon}
            </div>
            
            <div className="flex-1 gap-1">
              {title && <div className="text-sm font-semibold">{title}</div>}
              {description && (
                <div className="text-sm opacity-90">{description}</div>
              )}
            </div>

            <button
              onClick={() => dismiss(id)}
              className="absolute top-4 right-4 rounded-md p-1 opacity-50 transition-opacity hover:opacity-100 hover:bg-black/5"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )
      })}
    </div>
  )
}