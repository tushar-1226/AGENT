'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Brain, 
  Shield, 
  Zap, 
  Users, 
  TrendingUp, 
  TestTube, 
  Workflow,
  CheckCircle,
  AlertCircle,
  Clock,
  Target
} from 'lucide-react'

interface AgentCapability {
  name: string
  type: string
  capabilities: string[]
}

interface SecurityIssue {
  severity: string
  title: string
  description: string
  file_path: string
  line_number: number
}

interface PerformanceMetric {
  label: string
  duration_ms: number
  memory_delta_mb: number
}

export default function AdvancedFeaturesHub() {
  const [activeTab, setActiveTab] = useState('multi-agent')
  const [agents, setAgents] = useState<AgentCapability[]>([])
  const [securityScan, setSecurityScan] = useState<any>(null)
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  // Multi-Agent System
  const fetchAgentCapabilities = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/multi-agent/capabilities')
      const data = await response.json()
      if (data.success) {
        const agentsArray = Object.entries(data.capabilities).map(([name, caps]) => ({
          name,
          type: name,
          capabilities: caps as string[]
        }))
        setAgents(agentsArray)
      }
    } catch (error) {
      console.error('Error fetching agents:', error)
    }
    setLoading(false)
  }

  const processWithAgents = async (request: string) => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/multi-agent/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request, context: {} })
      })
      const data = await response.json()
      return data.result
    } catch (error) {
      console.error('Error processing with agents:', error)
    }
    setLoading(false)
  }

  // Security Copilot
  const runSecurityScan = async (code: string, filePath: string) => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/security/scan-file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, file_path: filePath })
      })
      const data = await response.json()
      if (data.success) {
        setSecurityScan(data.result)
      }
    } catch (error) {
      console.error('Error running security scan:', error)
    }
    setLoading(false)
  }

  // Predictive Analytics
  const fetchAnalytics = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/analytics/dashboard?days=30')
      const data = await response.json()
      if (data.success) {
        setAnalytics(data.dashboard)
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
    }
    setLoading(false)
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Advanced AI Features</h1>
          <p className="text-muted-foreground">
            Next-generation development tools powered by AI
          </p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-7 w-full">
          <TabsTrigger value="multi-agent">
            <Brain className="w-4 h-4 mr-2" />
            Agents
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="w-4 h-4 mr-2" />
            Security
          </TabsTrigger>
          <TabsTrigger value="testing">
            <TestTube className="w-4 h-4 mr-2" />
            Testing
          </TabsTrigger>
          <TabsTrigger value="analytics">
            <TrendingUp className="w-4 h-4 mr-2" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="performance">
            <Zap className="w-4 h-4 mr-2" />
            Performance
          </TabsTrigger>
          <TabsTrigger value="knowledge">
            <Users className="w-4 h-4 mr-2" />
            Knowledge
          </TabsTrigger>
          <TabsTrigger value="workflow">
            <Workflow className="w-4 h-4 mr-2" />
            Workflows
          </TabsTrigger>
        </TabsList>

        {/* Multi-Agent System Tab */}
        <TabsContent value="multi-agent" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Multi-Agent Orchestration System</CardTitle>
              <CardDescription>
                Specialized AI agents collaborate on complex tasks
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button onClick={fetchAgentCapabilities} disabled={loading}>
                Load Agent Capabilities
              </Button>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {agents.map((agent) => (
                  <Card key={agent.name}>
                    <CardHeader>
                      <CardTitle className="text-lg capitalize">{agent.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <p className="text-sm font-semibold">Capabilities:</p>
                        <div className="flex flex-wrap gap-2">
                          {agent.capabilities.map((cap) => (
                            <Badge key={cap} variant="secondary">
                              {cap.replace(/_/g, ' ')}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Copilot Tab */}
        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Copilot</CardTitle>
              <CardDescription>
                Real-time security vulnerability detection and compliance checking
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {securityScan && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Scan Results</h3>
                    <Badge 
                      variant={securityScan.security_score > 80 ? 'default' : 'destructive'}
                    >
                      Score: {securityScan.security_score}/100
                    </Badge>
                  </div>

                  <div className="grid grid-cols-4 gap-4">
                    {Object.entries(securityScan.by_severity || {}).map(([severity, count]) => (
                      <Card key={severity}>
                        <CardContent className="pt-6">
                          <div className="text-center">
                            <div className="text-2xl font-bold">{count as number}</div>
                            <div className="text-sm text-muted-foreground capitalize">
                              {severity}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  <div className="space-y-2">
                    {securityScan.vulnerabilities?.slice(0, 5).map((vuln: SecurityIssue, idx: number) => (
                      <div key={idx} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <AlertCircle className={`w-4 h-4 ${
                                vuln.severity === 'critical' ? 'text-red-500' :
                                vuln.severity === 'high' ? 'text-orange-500' :
                                vuln.severity === 'medium' ? 'text-yellow-500' :
                                'text-blue-500'
                              }`} />
                              <h4 className="font-semibold">{vuln.title}</h4>
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              {vuln.description}
                            </p>
                            <p className="text-xs text-muted-foreground mt-2">
                              {vuln.file_path}:{vuln.line_number}
                            </p>
                          </div>
                          <Badge variant="outline" className="capitalize">
                            {vuln.severity}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Testing Suite Tab */}
        <TabsContent value="testing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI-Powered Testing Suite</CardTitle>
              <CardDescription>
                Automated test generation, mutation testing, and coverage analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Unit Tests</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Button className="w-full">Generate Unit Tests</Button>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Coverage Analysis</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Button className="w-full">Analyze Coverage</Button>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Mutation Testing</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Button className="w-full">Run Mutation Tests</Button>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Predictive Analytics Dashboard</CardTitle>
              <CardDescription>
                DORA metrics, project forecasting, and developer productivity insights
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button onClick={fetchAnalytics} disabled={loading}>
                Load Analytics Dashboard
              </Button>

              {analytics && (
                <div className="space-y-6">
                  {/* DORA Metrics */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4">DORA Metrics</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <Card>
                        <CardContent className="pt-6">
                          <div className="text-center">
                            <Target className="w-8 h-8 mx-auto mb-2 text-blue-500" />
                            <div className="text-2xl font-bold">
                              {analytics.dora_metrics?.deployment_frequency?.rating || 'N/A'}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              Deployment Frequency
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="pt-6">
                          <div className="text-center">
                            <Clock className="w-8 h-8 mx-auto mb-2 text-green-500" />
                            <div className="text-2xl font-bold">
                              {analytics.dora_metrics?.lead_time?.rating || 'N/A'}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              Lead Time
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="pt-6">
                          <div className="text-center">
                            <Zap className="w-8 h-8 mx-auto mb-2 text-yellow-500" />
                            <div className="text-2xl font-bold">
                              {analytics.dora_metrics?.mttr?.rating || 'N/A'}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              MTTR
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="pt-6">
                          <div className="text-center">
                            <CheckCircle className="w-8 h-8 mx-auto mb-2 text-purple-500" />
                            <div className="text-2xl font-bold">
                              {analytics.dora_metrics?.change_failure_rate?.rating || 'N/A'}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              Change Failure Rate
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>

                  {/* Technical Debt */}
                  {analytics.technical_debt && (
                    <div>
                      <h3 className="text-lg font-semibold mb-4">Technical Debt</h3>
                      <Card>
                        <CardContent className="pt-6">
                          <div className="space-y-4">
                            <div className="flex items-center justify-between">
                              <span>Total Debt</span>
                              <span className="font-bold">
                                {analytics.technical_debt.total_days?.toFixed(1)} days
                              </span>
                            </div>
                            <Progress 
                              value={Math.min((analytics.technical_debt.total_hours / 100) * 100, 100)} 
                            />
                            <div className="text-sm text-muted-foreground">
                              {analytics.technical_debt.high_priority_items} high priority items
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Other tabs would follow similar patterns */}
        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <CardTitle>Performance Profiler</CardTitle>
              <CardDescription>
                Real-time performance monitoring and automatic optimization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Performance profiling interface coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="knowledge">
          <Card>
            <CardHeader>
              <CardTitle>Team Knowledge Graph</CardTitle>
              <CardDescription>
                Organizational knowledge base and expert finder
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Knowledge graph interface coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="workflow">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Automation</CardTitle>
              <CardDescription>
                Create custom automation rules with natural language
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Workflow automation interface coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
