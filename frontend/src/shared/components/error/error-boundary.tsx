"use client"

import React, { Component, ErrorInfo, ReactNode } from "react"
import { AlertTriangle, RefreshCcw, Home } from "lucide-react"
import { AppLayout } from "../../layouts/app-layout"

interface Props {
  children?: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
}

export class GlobalErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <div className="flex min-h-screen flex-col items-center justify-center p-4 text-center">
          <div className="mb-6 rounded-full bg-destructive/10 p-6 text-destructive">
            <AlertTriangle className="h-12 w-12" />
          </div>
          <h1 className="mb-2 text-2xl font-bold text-foreground">Something went wrong</h1>
          <p className="mb-8 max-w-md text-muted-foreground leading-relaxed">
            The application encountered an unexpected error. This has been logged and we're working to fix it.
          </p>
          <div className="flex gap-4">
            <button
              onClick={() => window.location.reload()}
              className="flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition-all hover:bg-primary/90"
            >
              <RefreshCcw className="h-4 w-4" />
              Reload Page
            </button>
            <button
              onClick={() => (window.location.href = "/")}
              className="flex items-center gap-2 rounded-lg border bg-background px-6 py-2.5 text-sm font-semibold text-foreground transition-all hover:bg-accent"
            >
              <Home className="h-4 w-4" />
              Back to Dashboard
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
