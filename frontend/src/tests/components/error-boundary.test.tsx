import { render, screen, fireEvent } from '@testing-library/react'
import { GlobalErrorBoundary } from '@/shared/components/error/error-boundary'
import { vi } from 'vitest'

const ThrowError = () => {
  throw new Error('Test Error')
}

describe('GlobalErrorBoundary Component', () => {
  // Prevent console.error from cluttering the test output
  beforeAll(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('renders fallback UI when an error occurs', () => {
    render(
      <GlobalErrorBoundary>
        <ThrowError />
      </GlobalErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText(/unexpected error/i)).toBeInTheDocument()
  })

  it('reloads page when reload button is clicked', () => {
    // Mock location.reload
    const originalLocation = window.location
    delete (window as any).location
    window.location = { ...originalLocation, reload: vi.fn() }

    render(
      <GlobalErrorBoundary>
        <ThrowError />
      </GlobalErrorBoundary>
    )

    const reloadButton = screen.getByText(/Reload Page/i)
    fireEvent.click(reloadButton)

    expect(window.location.reload).toHaveBeenCalled()

    // Cleanup
    window.location = originalLocation
  })
})
