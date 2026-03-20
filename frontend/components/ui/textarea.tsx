import * as React from "react"

import { cn } from "@/lib/utils"

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.ComponentProps<"textarea">
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    data-slot="textarea"
    className={cn(
      "flex min-h-[140px] w-full rounded-lg border bg-transparent px-3 py-2 text-sm leading-5 outline-none transition-colors placeholder:opacity-70 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
      className
    )}
    {...props}
  />
))

Textarea.displayName = "Textarea"

export { Textarea }
