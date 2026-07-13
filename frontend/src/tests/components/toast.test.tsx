import { render, screen, fireEvent } from '@testing-library/react'
import { Toast } from '@/shared/components/ui/toast'
import { vi } from 'vitest'

describe('Toast Component', () => {
  it('renders title and description correctly', () => {
    const mockOnClose = vi.fn()
    render(
      <Toast
        id="test-1"
        title="Success"
        description="Action completed"
        type="success"
        onClose={mockOnClose}
      />
    )

    expect(screen.getByText('Success')).toBeInTheDocument()
    expect(screen.getByText('Action completed')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    const mockOnClose = vi.fn()
    render(
      <Toast
        id="test-1"
        title="Info"
        type="info"
        onClose={mockOnClose}
      />
    )

    const closeButton = screen.getByRole('button')
    fireEvent.click(closeButton)

    expect(mockOnClose).toHaveBeenCalledWith('test-1')
  })
})
