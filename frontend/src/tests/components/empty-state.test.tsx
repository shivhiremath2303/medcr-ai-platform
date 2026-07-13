import { render, screen, fireEvent } from '@testing-library/react'
import { EmptyState } from '@/shared/components/ui/empty-state'
import { Search } from 'lucide-react'
import { vi } from 'vitest'

describe('EmptyState Component', () => {
  it('renders title and description', () => {
    render(
      <EmptyState
        icon={Search}
        title="No Results"
        description="Try a different query"
      />
    )

    expect(screen.getByText('No Results')).toBeInTheDocument()
    expect(screen.getByText('Try a different query')).toBeInTheDocument()
  })

  it('renders action button and handles click', () => {
    const mockOnClick = vi.fn()
    render(
      <EmptyState
        icon={Search}
        title="Empty"
        description="Nothing here"
        action={{
          label: 'Create New',
          onClick: mockOnClick
        }}
      />
    )

    const button = screen.getByText('Create New')
    fireEvent.click(button)

    expect(mockOnClick).toHaveBeenCalled()
  })
})
