import { render, screen, fireEvent } from '@testing-library/react'
import { CommandPalette } from '@/shared/components/command-palette/command-palette'
import { vi } from 'vitest'
import { useRouter } from 'next/navigation'

// Mock useRouter
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}))

describe('CommandPalette Component', () => {
  const mockPush = vi.fn()

  beforeEach(() => {
    (useRouter as any).mockReturnValue({
      push: mockPush,
    })
  })

  it('opens on Ctrl+K key press', () => {
    render(<CommandPalette />)

    // Simulate Ctrl+K
    fireEvent.keyDown(document, { key: 'k', ctrlKey: true })

    expect(screen.getByPlaceholderText(/Search pages/i)).toBeInTheDocument()
  })

  it('filters actions based on search input', () => {
    render(<CommandPalette />)
    fireEvent.keyDown(document, { key: 'k', ctrlKey: true })

    const input = screen.getByPlaceholderText(/Search pages/i)
    fireEvent.change(input, { target: { value: 'Admin' } })

    expect(screen.getByText('Admin Console')).toBeInTheDocument()
    // It should NOT show Dashboard if filtered by "Admin"
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
  })

  it('navigates to selected page and closes', () => {
    render(<CommandPalette />)
    fireEvent.keyDown(document, { key: 'k', ctrlKey: true })

    const adminAction = screen.getByText('Admin Console')
    fireEvent.click(adminAction)

    expect(mockPush).toHaveBeenCalledWith('/admin')
    expect(screen.queryByPlaceholderText(/Search pages/i)).not.toBeInTheDocument()
  })
})
