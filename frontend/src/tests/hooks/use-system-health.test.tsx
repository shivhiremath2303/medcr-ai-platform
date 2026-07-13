import { renderHook, waitFor } from '@testing-library/react'
import { useSystemHealth } from '@/features/admin/hooks/use-system-health'
import { adminApi } from '@/features/admin/api/admin-api'
import { vi } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactNode } from 'react'

// Mock adminApi
vi.mock('@/features/admin/api/admin-api', () => ({
  adminApi: {
    getHealth: vi.fn(),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useSystemHealth Hook', () => {
  it('fetches health data successfully', async () => {
    const mockData = { status: 'up', version: '1.0.0', environment: 'production' };
    (adminApi.getHealth as any).mockResolvedValue(mockData)

    const { result } = renderHook(() => useSystemHealth(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(result.current.data).toEqual(mockData)
  })

  it('handles fetch errors', async () => {
    (adminApi.getHealth as any).mockRejectedValue(new Error('Network error'))

    const { result } = renderHook(() => useSystemHealth(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isError).toBe(true))
  })
})
