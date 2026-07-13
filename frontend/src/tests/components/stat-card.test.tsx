import { render, screen } from '@testing-library/react'
import { StatCard } from '@/shared/components/dashboard/stat-card'
import { Files } from 'lucide-react'

describe('StatCard Component', () => {
  it('renders title, value, and description', () => {
    render(
      <StatCard
        title="Total Documents"
        value={124}
        icon={Files}
        description="Managed legal files"
      />
    )

    expect(screen.getByText('TOTAL DOCUMENTS')).toBeInTheDocument()
    expect(screen.getByText('124')).toBeInTheDocument()
    expect(screen.getByText('Managed legal files')).toBeInTheDocument()
  })

  it('renders positive trend correctly', () => {
    render(
      <StatCard
        title="Stats"
        value={10}
        icon={Files}
        trend={{ value: 12, isUp: true }}
      />
    )

    const trend = screen.getByText('+12%')
    expect(trend).toHaveClass('text-green-600')
  })

  it('renders negative trend correctly', () => {
    render(
      <StatCard
        title="Stats"
        value={10}
        icon={Files}
        trend={{ value: 5, isUp: false }}
      />
    )

    const trend = screen.getByText('-5%')
    expect(trend).toHaveClass('text-red-600')
  })
})
