import React from "react"

interface ErrorFallbackProps {
  error: Error
  resetErrorBoundary?: () => void
}

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetErrorBoundary,
}) => (
  <div>
    <h2>Something went wrong!</h2>
    <p>{error.message}</p>
    {resetErrorBoundary && (
      <button onClick={resetErrorBoundary}>Try again</button>
    )}
  </div>
)

interface Props {
  children?: React.ReactNode
  fallback: React.ComponentType<ErrorFallbackProps>
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
}

export class ErrorBoundary extends React.Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo)
    console.error(React.captureOwnerStack())
  }

  resetErrorBoundary = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  public render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback
      return (
        <FallbackComponent
          error={this.state.error!}
          resetErrorBoundary={this.resetErrorBoundary}
        />
      )
    }

    return this.props.children
  }
}
