"use client"

import { AppLayout } from "@/shared/layouts/app-layout"
import { PageHeader } from "@/shared/components/dashboard/page-header"
import { SettingsWorkspace } from "@/features/settings/components/settings-workspace"
import { motion } from "framer-motion"

export default function SettingsPage() {
  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <PageHeader
          title="Application Settings"
          description="Manage your account profile, appearance preferences, and platform notifications."
        />
      </motion.div>

      <SettingsWorkspace />
    </AppLayout>
  )
}
