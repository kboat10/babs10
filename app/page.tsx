import AuthWrapper from "@/components/auth-wrapper"
import { OrderBreakdownTool } from "@/components/order-breakdown-tool"

export default function Home() {
  return (
    <AuthWrapper>
      <OrderBreakdownTool />
    </AuthWrapper>
  )
}
