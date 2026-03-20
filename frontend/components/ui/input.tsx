import * as React from "react"

import { cn } from "@/lib/utils"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type = "text", ...props }, ref) => (
    <input
      ref={ref}
      type={type}
      data-slot="input"
      className={cn(
        "flex min-h-[44px] w-full rounded-lg border bg-transparent px-3 py-2 text-sm leading-5 outline-none transition-colors placeholder:opacity-70 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
        className
      )}
      {...props}
    />
  )
)

Input.displayName = "Input"

export { Input }
